import os
import glob
import json
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import tiktoken
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import PyPDF2
import io
#import docx

# — Initialization —
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL      = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBED_MODEL     = "text-embedding-ada-002"
COLLECTION_NAME = "linkedin_profiles"
MAX_TOKENS      = 2048

openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant = QdrantClient(url=QDRANT_URL)
encoding = tiktoken.encoding_for_model(EMBED_MODEL)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# — Data models —
class SearchRequest(BaseModel):
    query: str

class EmailRequest(BaseModel):
    profile: dict
    context: str

# — Utilities —
def chunk_by_tokens(text):
    ids = encoding.encode(text)
    for i in range(0, len(ids), MAX_TOKENS):
        yield encoding.decode(ids[i:i+MAX_TOKENS])

def profile_to_text(profile):
    parts = [f"{profile.get('name','')} — {profile.get('position','')}"]
    if about:=profile.get("about"): parts.append(about)
    curr = (profile.get("current_company") or {}).get("name")
    if curr: parts.append(f"Current: {curr}")
    exp = profile.get("experience") or []
    ent = [f"{e['title']} at {e['company']}" for e in exp if e.get("title") and e.get("company")]
    if ent: parts.append("Experience: " + "; ".join(ent))
    return "\n\n".join(parts)

# — On startup: ingest JSON -> Qdrant —
@app.on_event("startup")
def startup_event():
    profiles = []
    json_files = glob.glob("../linkedin_profiles_prod/linkedin_profiles_raw_*.json")
    print(f"Found {len(json_files)} JSON files to process")
    
    for path in json_files:
        print(f"Processing file: {path}")
        with open(path) as f:
            data = json.load(f)
            if isinstance(data, list):
                profiles.extend(data)
    
    print(f"Found {len(profiles)} profiles to embed")

    qdrant.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={"size": 1536, "distance": "Cosine"},
    )

    idx = 0
    points = []
    for p in profiles:
        if not p.get("id"): 
            print(f"Skipping profile without ID: {p.get('name', 'Unknown')}")
            continue
        txt = profile_to_text(p)
        for chunk_i, piece in enumerate(chunk_by_tokens(txt)):
            emb = openai_client.embeddings.create(model=EMBED_MODEL, input=piece).data[0].embedding
            payload = {
                "profile_id": p["id"],
                "current_company": (p.get("current_company") or {}).get("name"),
                "experience_companies": [e.get("company") for e in (p.get("experience") or []) if e.get("company")],
                "text": piece,
                "url": p.get("url"),
            }
            points.append(PointStruct(id=idx, vector=emb, payload=payload))
            idx += 1
            if len(points) >= 100:
                qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
                points = []
                print(f"Processed {idx} chunks so far")
    if points:
        qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"Final batch: processed {idx} chunks total")

@app.post("/api/search")
def search(req: SearchRequest):
    print(f"User query: {req.query}")
    qvec = openai_client.embeddings.create(model=EMBED_MODEL, input=req.query).data[0].embedding
    hits = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=qvec,
        limit=10,
        with_payload=True
    )
    print(f"Search returned {len(hits)} results")
    
    # Use a dictionary to deduplicate results by profile_id
    results_dict = {}
    for h in hits:
        p = h.payload
        profile_id = p.get("profile_id")
        if profile_id not in results_dict:  # Only add if we haven't seen this profile before
            text = p.get("text", "")
            lines = text.split("\\n\\n")
            if len(lines) > 0 and "—" in lines[0]:
                name, title = lines[0].split("—", 1)
            else:
                name, title = "Unknown", "Unknown"
            results_dict[profile_id] = {
                "name": name.strip(),
                "title": title.strip(),
                "bio": text,
                "profile_id": profile_id,
                "current_company": p.get("current_company"),
                "experience_companies": p.get("experience_companies"),
                "url": p.get("url"),
            }
    
    # Convert dictionary values back to list
    results = list(results_dict.values())
    return results

# — Endpoint: email generation —
async def extract_text_from_file(file: UploadFile) -> str:
    content = await file.read()
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif file_extension == 'txt':
        return content.decode('utf-8')
    elif file_extension == 'docx':
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

@app.post("/api/email")
async def email(
    profile: str = Form(...),
    context: str = Form(...),
    file: UploadFile = File(None)
):
    profile_dict = json.loads(profile) 
    file_context = ""
    if file:
        try:
            file_context = await extract_text_from_file(file)
            file_context = f"\nAdditional context from uploaded file:\n{file_context}"
        except Exception as e:
            return {"error": f"Error processing file: {str(e)}"}
    
    prompt = (
        f"Write a friendly, concise LinkedIn message to {profile_dict.get('profile_id', 'someone')} "
        f"({profile_dict.get('current_company', 'their current company')}).\n"
        f"You want to connect because {context}."
        f"{file_context}"
    )
    
    resp = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"email": resp.choices[0].message.content}

# — Endpoint: debug profiles —
@app.get("/api/debug-profiles")
def debug_profiles(limit: int = 5):
    hits = qdrant.scroll(
        collection_name=COLLECTION_NAME,
        limit=limit,
        with_payload=True
    )[0]
    return [h.payload for h in hits]