import json
import requests
import streamlit as st

API = "http://localhost:8000/api"

st.set_page_config(page_title="BearLink", page_icon="🐻")
st.markdown(
    """
    <style>
    .profile-card {
        background: rgba(0,0,0,0.1);
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    .profile-card h3 { margin: 0; font-size: 1.2rem; }
    .profile-card em { color: #888; font-size: 0.9rem; }
    .profile-card p { margin: 0.5rem 0 0.8rem; }
    </style>
    """,
    unsafe_allow_html=True
)

DEMO_PROFILES = [
    {"name": "Alice Sandy", "title": "Software Engineer at Amazon", "bio": "Built scalable systems on the backend."},
    {"name": "Bob Baskin", "title": "Data Scientist at Apple", "bio": "Specializes in ML for recommendation engines."},
    {"name": "Carol Christ",   "title": "Product Manager at Google", "bio": "Leads cross functional teams on mobile apps."},
]

def backend_search(query: str):
    resp = requests.post(f"{API}/search", json={"query": query})
    resp.raise_for_status()
    return resp.json()

def backend_generate_email(profile, context, uploaded_file):
    data = {
        "profile": json.dumps(profile),  # convert dict to string
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
    ("email_generated", "")
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.title("🐻 BearLink")

if st.session_state.stage == "search":
    query = st.text_input("🔍 Search the UC Berkeley Alumni Network")
    if st.button("Search"):
        st.session_state.search_results = backend_search(query)
        st.session_state.stage = "results"

elif st.session_state.stage == "results":
    if st.button("🔄 New Search"):
        st.session_state.stage = "search"
        st.session_state.search_results = []
        st.session_state.selected_profile = None
        st.session_state.compose_info = ""
        st.session_state.uploaded_file = None
        st.session_state.email_generated = ""

    st.subheader("Search Results")

    if not st.session_state.search_results:
        st.info("No profiles found for your query.")
    else:
        for idx, prof in enumerate(st.session_state.search_results):
            st.markdown(
                f"""
                <div class="profile-card">
                    <h3>{prof['name']}</h3>
                    <em>{prof['title']}</em>
                    <p>{prof['bio']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            first_name = prof["name"].split()[0]
            if st.button(f"Reach out to {first_name}", key=f"reach_{idx}"):
                st.session_state.selected_profile = prof
                st.session_state.stage = "confirm"

elif st.session_state.stage == "confirm":
    prof = st.session_state.selected_profile
    st.write(f"Would you like me to write an email to **{prof['name']}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes"):
            st.session_state.stage = "compose"
    with col2:
        if st.button("No"):
            st.session_state.stage = "search"
            st.session_state.search_results = []
            st.session_state.selected_profile = None

elif st.session_state.stage == "compose":
    prof = st.session_state.selected_profile
    st.subheader(f"Compose email to {prof['name']}")

    st.text_area(
        "Additional details or context:",
        value=st.session_state.compose_info,
        key="compose_info",
        height=100
    )

    st.file_uploader(
        "Upload a document (e.g., resume):",
        type=["pdf"],
        key="uploaded_file"
    )
    if st.session_state.uploaded_file is not None:
        st.write(f"**Currently uploaded:** {st.session_state.uploaded_file.name}")

    if st.button("Generate Email"):
        st.session_state.email_generated = backend_generate_email(
            prof,
            st.session_state.compose_info,
            st.session_state.uploaded_file
        )
        st.session_state.stage = "done"

elif st.session_state.stage == "done":
    st.subheader("Generated Email")
    st.text_area(
        "Your draft email",
        value=st.session_state.email_generated,
        height=300,
        label_visibility="hidden"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Regenerate Email"):
            st.session_state.email_generated = backend_generate_email(
                st.session_state.selected_profile,
                st.session_state.compose_info,
                st.session_state.uploaded_file
            )
    with col2:
        if st.button("Edit Email Context"):
            st.session_state.stage = "compose"
    with col3:
        if st.button("Start New Search"):
            for k in ["stage","search_results","selected_profile",
                      "compose_info","uploaded_file","email_generated"]:
                st.session_state.pop(k, None)
            st.session_state.stage = "search"
