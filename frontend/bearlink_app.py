import json
import requests
import streamlit as st
import time

API = "http://localhost:8000/api"

st.set_page_config(
    page_title="BearLink",
    page_icon="🐻",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .profile-card {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        color: var(--text-color);
    }
    .profile-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    }
    .profile-card h3 { 
        margin: 0; 
        font-size: 1.4rem;
        color: var(--primary-color);
    }
    .profile-card em { 
        color: var(--secondary-background-color);
        font-size: 1rem;
        display: block;
        margin: 0.5rem 0;
    }
    .profile-card p { 
        margin: 0.8rem 0;
        color: var(--text-color);
        line-height: 1.5;
    }
    .stButton button {
        width: 100%;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .search-box {
        background: rgba(255,255,255,0.1);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: var(--text-color);
    }
    .email-preview {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
        color: var(--text-color);
    }
    .reachout-cool {
        background: linear-gradient(90deg, #003262 60%, #FDB515 100%);
        color: white;
        border: none;
        border-radius: 0.7rem;
        padding: 0.7rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0,50,98,0.10);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: background 0.2s, transform 0.2s;
    }
    .reachout-cool:hover {
        background: linear-gradient(90deg, #002147 60%, #FFD700 100%);
        transform: translateY(-2px) scale(1.03);
        color: #003262;
    }
    .back-to-search-btn {
        background: #eee;
        color: #003262;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        margin-top: 0.5rem;
        cursor: pointer;
        transition: background 0.2s, color 0.2s;
    }
    .back-to-search-btn:hover {
        background: #003262;
        color: #fff;
    }
    h1 {
        margin-bottom: 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    st.image("assets/img/satherTower.png", width=200)
    st.title("BearLink")
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Discover and reach out to the UC Berkeley Alumni Network through personalized messages.")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("1. Find fellow Berkeley alumni in any avenue you are interested in")
    st.markdown("2. Choose someone to reach out to")
    st.markdown("3. Share your Berkeley story and any experiences and upload relevant documents")
    st.markdown("4. Get a personalized message to start the conversation")

DEMO_PROFILES = [
    {"name": "Alice Sandy", "title": "Software Engineer at Amazon", "bio": "Built scalable systems on the backend."},
    {"name": "Bob Baskin", "title": "Data Scientist at Apple", "bio": "Specializes in ML for recommendation engines."},
    {"name": "Carol Christ",   "title": "Product Manager at Google", "bio": "Leads cross functional teams on mobile apps."},
]

def backend_search(query: str):
    resp = requests.post(f"{API}/search", json={"query": query})
    resp.raise_for_status()
    results = resp.json()
    
    seen_ids = set()
    unique_results = []
    for result in results:
        profile_id = result.get('profile_id')
        if profile_id and profile_id not in seen_ids:
            seen_ids.add(profile_id)
            unique_results.append(result)
    
    return unique_results

def backend_generate_email(profile, context, uploaded_file):
    data = {
        "profile": json.dumps(profile), 
        "context": context
    }
    files = {}
    if uploaded_file is not None:
        files["file"] = (uploaded_file.name, uploaded_file.getvalue())

    resp = requests.post(f"{API}/email", data=data, files=files)
    resp.raise_for_status()
    return resp.json()["email"]

for key, default in [
    ("stage", "search"),
    ("search_results", []),
    ("selected_profile", None),
    ("compose_info", ""),
    ("uploaded_file", None),
    ("email_generated", ""),
    ("is_loading", False),
    ("search_query", "")
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("🐻 BearLink")

if st.session_state.stage == "search":
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    st.markdown("### Find Your Fellow Golden Bear Alumni Network")
    query = st.text_input(
        "What are you looking for?",
        key="search_input",
        placeholder="'Haas MBA graduates', 'Berkeley research in AI', 'Department of Music alumni'"
    )
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Find Bears", use_container_width=True):
            if query.strip():
                st.session_state.search_query = query
                st.session_state.is_loading = True
                st.session_state.stage = "loading_search"
                st.rerun()
            else:
                st.warning("Please tell us what you're looking for")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.stage == "loading_search":
    with st.spinner("🔍 Finding your fellow Golden Bears..."):
        try:
            st.session_state.search_results = backend_search(st.session_state.search_query)
            st.session_state.is_loading = False
            st.session_state.stage = "results"
            st.rerun()
        except Exception as e:
            st.error(f"Error during search: {str(e)}")
            st.session_state.is_loading = False
            st.session_state.stage = "search"
            st.rerun()

elif st.session_state.stage == "results":
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 New Search", use_container_width=True):
            #clear all relevant state
            st.session_state.search_results = []
            st.session_state.selected_profile = None
            st.session_state.compose_info = ""
            st.session_state.uploaded_file = None
            st.session_state.email_generated = ""
            st.session_state.search_query = ""
            st.session_state.is_loading = False
            st.session_state.stage = "search"
            st.rerun()

    st.markdown("### Found Bears")
    if not st.session_state.search_results:
        st.info("No matching profiles found. Try different keywords or broaden your search.")
    else:
        st.markdown(f"Found {len(st.session_state.search_results)} fellow Golden Bears matching your search")
        for idx, prof in enumerate(st.session_state.search_results):
            bio_text = prof['bio']
            parts = bio_text.split("\\n\\n")
            display_bio_parts = parts[1:] if len(parts) > 1 else []
            clean_bio = "\n\n".join(display_bio_parts)
            
            st.markdown(
                f"""
                <div class="profile-card">
                    <h3><a href="{prof.get('url', '#')}" target="_blank" style="text-decoration:none; color:inherit;">{prof['name']}</a></h3>
                    <em>{prof['title']}</em>
                    <p>{clean_bio}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            first_name = prof["name"].split()[0]

            if st.button(f"🤝 Reach out to {first_name}", key=f"reach_{idx}", use_container_width=True):
                st.session_state.selected_profile = prof
                st.session_state.stage = "confirm"
                st.rerun()

elif st.session_state.stage == "confirm":
    prof = st.session_state.selected_profile
    st.markdown(f"### Would you like to reach out to {prof['name']}?")
    st.markdown(f"**Current Role:** {prof['title']}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, help me reach out", use_container_width=True):
            st.session_state.stage = "compose"
            st.rerun()
    with col2:
        if st.button("No, find other searches", use_container_width=True):

            st.session_state.search_results = []
            st.session_state.selected_profile = None
            st.session_state.stage = "search"
            st.rerun()

elif st.session_state.stage == "compose":
    prof = st.session_state.selected_profile
    st.markdown(f"### Compose message to {prof['name']}")
    
    st.markdown("#### Additional Context")
    st.markdown("Tell us why you want to reach out (such as any shared interests, career advice, networking)")
    context = st.text_area(
        "Your message context:",
        value=st.session_state.compose_info,
        key="compose_info",
        height=100,
        placeholder="I'm interested in reaching out because..."
    )

    st.markdown("#### Upload Documents (Optional)")
    st.markdown("Upload any relevant documents to help generate a more personalized message")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "txt", "doc", "docx"],
        key="uploaded_file",
        help="Upload any relevant documents (PDF, TXT, DOCX)"
    )
    if uploaded_file is not None:
        st.success(f"✅ Uploaded: {uploaded_file.name}")

    if st.button("Generate Message", use_container_width=True):
        st.session_state.stage = "loading_email"
        st.rerun()

    if st.button("⬅️ Back to Search", key="back_to_search", use_container_width=True):
        for k in ["stage","search_results","selected_profile",
                  "compose_info","uploaded_file","email_generated",
                  "is_loading","search_query"]:
            st.session_state.pop(k, None)
        st.session_state.stage = "search"
        st.rerun()

elif st.session_state.stage == "loading_email":
    with st.spinner("✍️ Writing your personalized message..."):
        try:
            st.session_state.email_generated = backend_generate_email(
                st.session_state.selected_profile,
                st.session_state.compose_info,
                st.session_state.uploaded_file
            )
            st.session_state.stage = "done"
            st.rerun()
        except Exception as e:
            st.error(f"Error generating message: {str(e)}")
            st.session_state.stage = "compose"
            st.rerun()

elif st.session_state.stage == "done":
    st.markdown("### Your Personalized Message")
    st.markdown('<div class="email-preview">', unsafe_allow_html=True)
    st.text_area(
        "Message preview",
        value=st.session_state.email_generated,
        height=300,
        label_visibility="hidden"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Regenerate", use_container_width=True):
            st.session_state.stage = "loading_email"
            st.rerun()
    with col2:
        if st.button("✏️ Edit Context", use_container_width=True):
            st.session_state.stage = "compose"
            st.rerun()
    with col3:
        if st.button("🔍 New Search", use_container_width=True):
            # Clear all state
            for k in ["stage","search_results","selected_profile",
                      "compose_info","uploaded_file","email_generated",
                      "is_loading","search_query"]:
                st.session_state.pop(k, None)
            st.session_state.stage = "search"
            st.rerun()
