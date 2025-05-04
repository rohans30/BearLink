# bearlink_app.py
import streamlit as st

st.set_page_config(page_title="BearLink", page_icon="🐻")

def backend_response(query: str) -> str:
    normalized = query.lower().strip()
    ### back end stuff

    # default reply for right now
    return (
        "Hello, the result would display here. This is just a placeholder until the real backend is connected."
    )


st.title("🐻 BearLink")

if "messages" not in st.session_state:
    st.session_state.messages = []       


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_query := st.chat_input("Ask me something about the UC Berkeley Alumni network..."):

    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
        
    assistant_reply = backend_response(user_query)
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)
