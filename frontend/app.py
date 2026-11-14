
import os

import requests
import streamlit as st


# ==========================================
# Configuration
# ==========================================

API_URL = os.getenv(
    "DOCUMIND_API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================
# Session State
# ==========================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "flash_message" not in st.session_state:
    st.session_state.flash_message = None


# ==========================================
# API Helper
# ==========================================

def api_request(method, endpoint, **kwargs):
    """
    Send a request to the FastAPI backend.

    Returns:
        (success, data)
    """

    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=120,
            **kwargs,
        )

        response.raise_for_status()

        if not response.content:
            return True, None

        return True, response.json()

    except requests.exceptions.RequestException as exc:
        detail = str(exc)

        if exc.response is not None:
            try:
                error_data = exc.response.json()

                if isinstance(error_data, dict):
                    detail = error_data.get(
                        "detail",
                        detail,
                    )
            except ValueError:
                pass

        st.error(f"API request failed: {detail}")
        return False, None

    except ValueError:
        st.error("The API returned invalid JSON.")
        return False, None


# ==========================================
# Document Helpers
# ==========================================

def load_documents():
    success, result = api_request(
        "GET",
        "/documents",
    )

    if not success:
        return []

    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        return result.get("documents", [])

    return []


def get_document_options(documents):
    options = {}

    for doc in documents:
        label = (
            f"{doc['id']} — "
            f"{doc.get('title', 'Untitled')}"
        )

        options[label] = doc["id"]

    return options


def show_sources(sources):
    if not sources:
        st.info("No sources available.")
        return

    for index, source in enumerate(
        sources,
        start=1,
    ):
        title = source.get(
            "document_title",
            "Untitled",
        )

        chunk_index = source.get(
            "chunk_index",
            "?",
        )

        similarity = source.get(
            "similarity",
            0,
        )

        with st.expander(
            f"[Source {index}] {title} "
            f"— Chunk {chunk_index}"
        ):
            st.caption(
                f"Document ID: "
                f"{source.get('document_id', '?')}"
            )

            st.caption(
                f"Similarity: {similarity:.3f}"
            )

            st.write(
                source.get("content", "")
            )


# ==========================================
# Sidebar
# ==========================================

st.sidebar.title("📚 DocuMind")
st.sidebar.caption(
    "AI-Powered Document Knowledge Base"
)

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

st.sidebar.caption(
    "FastAPI · PostgreSQL · pgvector"
)

st.sidebar.caption(
    "Gemini Flash Lite · Streamlit"
)


# ==========================================
# Load Documents
# ==========================================

documents = load_documents()
document_options = get_document_options(
    documents
)

if st.session_state.flash_message:
    st.success(
        st.session_state.flash_message
    )

    st.session_state.flash_message = None


# ==========================================
# Dashboard
# ==========================================

if page == "Dashboard":

    st.title("📚 DocuMind Dashboard")

    st.write(
        "Manage your AI-powered document library."
    )

    total_documents = len(documents)

    ready_documents = sum(
        1
        for doc in documents
        if doc.get("status") == "ready"
    )

    pending_documents = sum(
        1
        for doc in documents
        if doc.get("status") == "pending"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Documents",
        total_documents,
    )

    col2.metric(
        "Ready Documents",
        ready_documents,
    )

    col3.metric(
        "Pending Documents",
        pending_documents,
    )

    st.divider()

    st.subheader("Document Library")

    if not documents:
        st.info(
            "No documents found. "
            "Upload your first PDF."
        )

    else:
        for doc in documents:

            with st.container(border=True):

                col1, col2 = st.columns(
                    [5, 1]
                )

                with col1:

                    st.markdown(
                        f"**{doc.get('title', 'Untitled')}**"
                    )

                    page_count = doc.get(
                        "page_count"
                    )

                    if page_count is None:
                        page_count = "N/A"

                    st.caption(
                        f"ID: {doc['id']} | "
                        f"Status: "
                        f"{doc.get('status', 'unknown')} | "
                        f"Pages: {page_count}"
                    )

                with col2:

                    with st.popover(
                        "Delete",
                        icon="🗑️",
                    ):

                        st.warning(
                            "This action permanently "
                            "deletes the document."
                        )

                        st.write(
                            f"Delete "
                            f"**{doc.get('title', 'Untitled')}**?"
                        )

                        if st.button(
                            "Confirm Delete",
                            key=(
                                f"confirm_delete_"
                                f"{doc['id']}"
                            ),
                            type="primary",
                        ):

                            success, _ = api_request(
                                "DELETE",
                                f"/documents/{doc['id']}",
                            )

                            if success:

                                st.session_state.flash_message = (
                                    "Document deleted successfully."
                                )

                                st.rerun()


# ==========================================
# Upload PDF
# ==========================================

elif page == "Upload PDF":

    st.title("📤 Upload PDF")

    st.write(
        "Upload a PDF to extract its text, "
        "create chunks, and generate embeddings."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
    )

    title = st.text_input(
        "Document title (optional)"
    )

    if uploaded_file is not None:

        st.caption(
            f"Selected file: "
            f"{uploaded_file.name}"
        )

        file_size_mb = (
            uploaded_file.size
            / (1024 * 1024)
        )

        st.caption(
            f"File size: "
            f"{file_size_mb:.2f} MB"
        )

        if file_size_mb > 10:

            st.error(
                "File size must not exceed 10 MB."
            )

        elif st.button(
            "Upload and Process",
            type="primary",
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

            with st.spinner(
                "Processing PDF and "
                "generating embeddings..."
            ):

                success, result = api_request(
                    "POST",
                    "/documents/upload",
                    files=files,
                    data=data,
                )

            if success:

                st.success(
                    "PDF uploaded successfully!"
                )

                if result is not None:
                    st.json(result)

                st.info(
                    "Open Dashboard to view "
                    "your updated document library."
                )


# ==========================================
# Semantic Search
# ==========================================

elif page == "Semantic Search":

    st.title("🔎 Semantic Search")

    st.write(
        "Find relevant passages "
        "using vector similarity."
    )

    query = st.text_input(
        "Search your documents",
        placeholder=(
            "What is a string in Python?"
        ),
    )

    selected_document = st.selectbox(
        "Search scope",
        ["All documents"]
        + list(document_options),
    )

    top_k = st.slider(
        "Number of results",
        min_value=1,
        max_value=10,
        value=5,
        key="search_top_k",
    )

    if st.button(
        "Search",
        type="primary",
    ):

        if not query.strip():

            st.warning(
                "Please enter a search query."
            )

        else:

            payload = {
                "query": query,
                "top_k": top_k,
                "document_id": (
                    document_options.get(
                        selected_document
                    )
                ),
            }

            with st.spinner(
                "Searching documents..."
            ):

                success, result = api_request(
                    "POST",
                    "/search",
                    json=payload,
                )

            if success and isinstance(
                result,
                dict,
            ):

                matches = result.get(
                    "results",
                    [],
                )

                st.subheader(
                    f"Found {len(matches)} results"
                )

                if not matches:

                    st.info(
                        "No matching document "
                        "passages were found."
                    )

                else:

                    for index, match in enumerate(
                        matches,
                        start=1,
                    ):

                        title = match.get(
                            "document_title",
                            "Untitled",
                        )

                        similarity = match.get(
                            "similarity",
                            0,
                        )

                        with st.expander(
                            f"Result {index} — "
                            f"{title} "
                            f"(Similarity: "
                            f"{similarity:.3f})"
                        ):

                            st.write(
                                match.get(
                                    "content",
                                    "",
                                )
                            )

                            st.caption(
                                f"Document ID: "
                                f"{match.get('document_id')} | "
                                f"Chunk: "
                                f"{match.get('chunk_index')}"
                            )


# ==========================================
# Ask AI (RAG)
# ==========================================

elif page == "Ask AI":

    st.title("🤖 Ask Your Documents")

    st.write(
        "Ask questions and receive "
        "AI-generated answers grounded "
        "in your uploaded PDFs."
    )

    selected_document = st.selectbox(
        "Choose document",
        ["All documents"]
        + list(document_options),
    )

    top_k = st.slider(
        "Sources to retrieve",
        min_value=1,
        max_value=10,
        value=5,
        key="ask_top_k",
    )

    st.divider()

    # Display existing chat history
    for chat in st.session_state.chat_history:

        with st.chat_message("user"):
            st.write(
                chat["question"]
            )

        with st.chat_message("assistant"):

            st.markdown(
                chat["answer"]
            )

            with st.expander(
                "View Sources"
            ):
                show_sources(
                    chat["sources"]
                )

    # New question
    question = st.chat_input(
        "Ask a question about your documents..."
    )

    if question:

        payload = {
            "question": question,
            "top_k": top_k,
            "document_id": (
                document_options.get(
                    selected_document
                )
            ),
        }

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):

            with st.spinner(
                "Searching documents "
                "and asking Gemini..."
            ):

                success, result = api_request(
                    "POST",
                    "/ask",
                    json=payload,
                )

            if success and isinstance(
                result,
                dict,
            ):

                answer = result.get(
                    "answer",
                    "",
                )

                sources = result.get(
                    "sources",
                    [],
                )

                st.markdown(answer)

                with st.expander(
                    "View Sources"
                ):
                    show_sources(sources)

                st.session_state.chat_history.append({
                    "question": question,
                    "answer": answer,
                    "sources": sources,
                })

    st.divider()

    if st.button(
        "Clear Chat History",
        icon="🗑️",
    ):

        st.session_state.chat_history = []

        st.rerun()
