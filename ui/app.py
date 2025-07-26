# ui/app.py

import streamlit as st
import requests

st.set_page_config(page_title="📄 Agentic RAG Chatbot", layout="wide")

st.title("📄 Agentic RAG Chatbot")
st.markdown("Upload documents and ask questions. Chat history is now supported.")

# === Session storage ===
if "history" not in st.session_state:
    st.session_state.history = []

uploaded_files = st.file_uploader(
    "Upload documents (PDF, DOCX, PPTX, CSV, TXT, MD)",
    type=["pdf", "docx", "pptx", "csv", "txt", "md"],
    accept_multiple_files=True
)

query = st.text_input("Enter your question:")

if st.button("Ask"):
    if not uploaded_files or not query:
        st.warning("Please upload files and ask a question.")
    else:
        # Prepare files and chat history
        files = [("files", (f.name, f, f.type)) for f in uploaded_files]
        data = {
            "query": query,
            "history": str(st.session_state.history)  # send as string
        }

        with st.spinner("Thinking..."):
            try:
                res = requests.post("http://localhost:8000/process", files=files, data=data)
                if res.status_code == 200:
                    msg = res.json()

                    # Save new turn
                    st.session_state.history.append({
                        "query": msg["payload"]["query"],
                        "answer": msg["payload"]["answer"]
                    })

                    # Show result
                    st.success("Answer:")
                    st.markdown(f"**Q:** {msg['payload']['query']}")
                    st.markdown(f"**A:** {msg['payload']['answer']}")

                    with st.expander("📄 Source Chunks"):
                        for chunk in msg["payload"]["sources"]:
                            st.markdown(f"- {chunk}")

                else:
                    st.error("Backend error.")
            except Exception as e:
                st.error(f"Request failed: {e}")

# === Chat history ===
st.divider()
st.subheader("📜 Chat History")
for turn in st.session_state.history:
    st.markdown(f"**You:** {turn['query']}")
    st.markdown(f"**Bot:** {turn['answer']}")
