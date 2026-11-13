
import os
import requests
import streamlit as st

API_URL = os.getenv(
    "DOCUMIND_API_URL",
    "http://127.0.0.1:8000",
)

st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide",
)

# -----------------------------
# API helper
# -----------------------------
def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=120,
            **kwargs,
        )
        response.raise_for_status()

        if response.status_code == 204:
            return None

        if not response.content:
            return None

        return response.json()

    except requests.exceptions.RequestException as exc:
        detail = str(exc)

        if exc.response is not None:
            try:
                detail = exc.response.json().get(
                    "detail", detail
                )
            except ValueError:
                pass

        st.error(f"API request failed: {detail}")
        return None


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📚 DocuMind")
st.sidebar.caption("AI Document Knowledge Base")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Upload PDF",
        "Semantic Search",
        "Ask AI",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Powered by FastAPI + Gemini")


# -----------------------------
# Load documents
# -----------------------------
def load_documents():
    result = api_request("GET", "/documents")

    if isinstance(result, list):
        return result

    # Also support a wrapped API response.
    if isinstance(result, dict):
        return result.get("documents", [])

    return []


documents = load_documents()

document_options = {
    f"{doc['id']} — {doc['title']}": doc["id"]
    for doc in documents
}


# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
    st.title("DocuMind Dashboard")
    st.write("Manage your AI-powered document library.")

    total_documents = len(documents)

    ready_documents = sum(
        1 for doc in documents
        if doc.get("status") == "ready"
    )

    col1, col2 = st.columns(2)

    col1.metric("Total Documents", total_documents)
    col2.metric("Ready Documents", ready_documents)

    st.subheader("Document Library")

    if not documents:
        st.info("No documents found. Upload your first PDF.")

    else:
        for doc in documents:
            with st.container(border=True):
                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(
                        f"**{doc.get('title', 'Untitled')}**"
                    )
                    st.caption(
                        f"ID: {doc['id']} | "
                        f"Status: {doc.get('status', 'unknown')} | "
                        f"Pages: {doc.get('page_count', 'N/A')}"
                    )

                with col2:
                    if st.button(
                        "Delete",
                        key=f"delete_{doc['id']}",
                    ):
                        result = api_request(
                            "DELETE",
                            f"/documents/{doc['id']}",
                        )

                        # A successful DELETE may return
                        # 204 No Content, so None is normal.
                        st.rerun()


# -----------------------------
# Upload PDF
# -----------------------------
elif page == "Upload PDF":
    st.title("Upload PDF")
    st.write(
        "Upload a PDF to extract text, "
        "generate embeddings, and enable AI search."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"],
    )

    title = st.text_input(
        "Document title (optional)"
    )

    if uploaded_file is not None:
        st.caption(
            f"Selected: {uploaded_file.name}"
        )

        if st.button(
            "Upload and Process",
            type="primary",
        ):
            with st.spinner(
                "Processing PDF and generating embeddings..."
            ):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf",
                    )
                }

                data = {}

                if title.strip():
                    data["title"] = title.strip()

                result = api_request(
                    "POST",
                    "/documents/upload",
                    files=files,
                    data=data,
                )

            if result is not None:
                st.success("PDF uploaded successfully!")
                st.json(result)


# -----------------------------
# Semantic Search
# -----------------------------
elif page == "Semantic Search":
    st.title("Semantic Search")
    st.write(
        "Find relevant passages using vector similarity."
    )

    query = st.text_input(
        "Search your documents",
        placeholder="What is a string in Python?",
    )

    selected_document = st.selectbox(
        "Search scope",
        ["All documents"] + list(document_options),
    )

    top_k = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=5,
    )

    if st.button("Search", type="primary"):
        if not query.strip():
            st.warning("Please enter a search query.")

        else:
            payload = {
                "query": query,
                "top_k": top_k,
                "document_id": document_options.get(
                    selected_document
                ),
            }

            with st.spinner("Searching..."):
                result = api_request(
                    "POST",
                    "/search",
                    json=payload,
                )

            if result is not None:
                matches = result.get("results", [])

                st.subheader(
                    f"Found {len(matches)} results"
                )

                for index, match in enumerate(
                    matches, start=1
                ):
                    with st.expander(
                        f"Result {index} — "
                        f"{match['document_title']} "
                        f"(Similarity: "
                        f"{match['similarity']:.3f})"
                    ):
                        st.write(match["content"])
                        st.caption(
                            f"Document ID: "
                            f"{match['document_id']} | "
                            f"Chunk: {match['chunk_index']}"
                        )


# -----------------------------
# Ask AI (RAG)
# -----------------------------
elif page == "Ask AI":
    st.title("Ask Your Documents")
    st.write(
        "Ask questions and get answers grounded "
        "in your uploaded PDFs."
    )

    question = st.text_area(
        "Your question",
        placeholder=(
            "Explain Python strings based "
            "on my uploaded documents."
        ),
        height=120,
    )

    selected_document = st.selectbox(
        "Choose document",
        ["All documents"] + list(document_options),
    )

    top_k = st.slider(
        "Sources to retrieve",
        min_value=1,
        max_value=10,
        value=5,
    )

    if st.button("Ask Gemini", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")

        else:
            payload = {
                "question": question,
                "top_k": top_k,
                "document_id": document_options.get(
                    selected_document
                ),
            }

            with st.spinner(
                "Searching documents and generating answer..."
            ):
                result = api_request(
                    "POST",
                    "/ask",
                    json=payload,
                )

            if result is not None:
                st.subheader("AI Answer")
                st.markdown(result.get("answer", ""))

                sources = result.get("sources", [])

                st.subheader(
                    f"Sources ({len(sources)})"
                )

                for index, source in enumerate(
                    sources, start=1
                ):
                    with st.expander(
                        f"Source {index} — "
                        f"{source['document_title']}"
                    ):
                        st.write(source["content"])
                        st.caption(
                            f"Similarity: "
                            f"{source['similarity']:.3f} | "
                            f"Chunk: {source['chunk_index']}"
                        )
