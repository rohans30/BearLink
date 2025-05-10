# BearLink
CS 294-280 Project

BearLink is a networking tool specifically for UC Berkeley students and alumni to build professional connections through intelligent search and personalized outreach features.
The front-end built with StreamLit is in `frontend/bearlink_app.py`. The back-end FastAPI service in `backend/app.py` powers a RAG pipeline using Qdrant + OpenAI under the hood.

---

## Repository Layout

```
bearlink/
├── .env.example
├── environment.yml       # Conda spec (preferred)
├── requirements.txt      # pip spec (optional)
├── README.md
├── backend/
│   └── app.py
└── frontend/
    └── bearlink_app.py
```

---

## Prerequisites

- **Python 3.10+**
- **Conda** (recommended) _or_ **pip + virtualenv**
- **Docker** (for Qdrant)
- An **OpenAI API key**

---

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-org/BearLink.git
   cd BearLink
   ```

2. **Copy and fill your API key**
   ```bash
   cp .env.example .env
   # → Open `.env` and set your OPENAI_API_KEY, QDRANT_URL if necessary
   ```

3A. **(Recommended) Create & activate Conda env**
   ```bash
   conda env create -f environment.yml
   conda activate bearlink
   ```

3B. **(Alternative) Create & activate a venv + pip**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # or `.venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

---

## Start Qdrant

Run Qdrant locally in Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```
> **Tip:** If you use Qdrant Cloud, set `QDRANT_URL` in your `.env` accordingly.

---

## Running the Backend

```bash
cd backend
# For development:
uvicorn app:app --reload
# For production:
# Will need to manually restart the server on code changes
uvicorn app:app
```
- **API endpoints**
  - `POST /api/search` ── JSON `{ "query": "<your search>" }`
  - `POST /api/email`  ── JSON `{ "profile": {...}, "context": "..." }` + optional file upload

---

## Running the Frontend

```bash
cd frontend
streamlit run bearlink_app.py
```
- Opens at `http://localhost:8501` by default
- Use the UI to search profiles, select one, and generate a LinkedIn message.

---

## .env.example

```dotenv
# Copy this file to .env and fill in your values

OPENAI_API_KEY=your-openai-api-key-here
QDRANT_URL=http://localhost:6333
```

---

## License

This project is released under the MIT License.

Developed by the BearLink Team: Rohan Srivastava, Arjun Manoj, Satwika Paul, Amrutha Srivatsav