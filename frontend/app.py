
import os
import html
import requests
import streamlit as st

API_URL = os.getenv(
    "DOCUMIND_API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

st.set_page_config(
    page_title="DocuMind — Knowledge Workspace",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------
# STATE
# -----------------------------------------

defaults = {
    "page": "Overview",
    "chat_history": [],
    "search_results": None,
    "flash": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -----------------------------------------
# STYLES
# -----------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #171D2B;
    --muted: #788397;
    --border: #E9EDF3;
    --accent: #4F46E5;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #FFFFFF;
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #FAFBFD;
    border-right: 1px solid #E9EDF3;
    min-width: 255px;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 2rem 1.15rem;
}

.block-container {
    max-width: 1320px;
    padding: 2.5rem 3.5rem 5rem;
}

h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    letter-spacing: -.045em;
    color: #171D2B;
}

h1 {
    font-size: 2.15rem !important;
    font-weight: 800 !important;
}

h2 {
    font-size: 1.25rem !important;
    font-weight: 750 !important;
}

p {
    color: #586478;
}

[data-testid="stVerticalBlockBorderWrapper"] > div {
    border: 1px solid #E9EDF3 !important;
    border-radius: 14px !important;
    background: #FFFFFF;
}

[data-testid="stMetric"] {
    padding: 20px 22px;
    border: 1px solid #E9EDF3;
    border-radius: 14px;
    background: #FFFFFF;
}

[data-testid="stMetricLabel"] {
    color: #788397;
    font-size: .82rem;
}

[data-testid="stMetricValue"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 2rem;
    color: #171D2B;
}

.stButton > button {
    border-radius: 9px;
    font-weight: 600;
    border-color: #E5EAF1;
    transition: .15s;
}

.stButton > button[kind="primary"] {
    background: #4F46E5;
    border-color: #4F46E5;
    color: white;
}

.stButton > button[kind="primary"]:hover {
    background: #4338CA;
    border-color: #4338CA;
    color: white;
}

[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    justify-content: flex-start;
    border: none;
    background: transparent;
    color: #586478;
    padding: 12px 14px;
    box-shadow: none;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #EEF0F8;
    color: #252A44;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #EBEBFF;
    color: #4338CA;
    border: none;
}

[data-testid="stFileUploaderDropzone"] {
    background: #FAFBFF;
    border: 1.5px dashed #B8C3D8;
    border-radius: 12px;
    padding: 30px;
}

[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid #E9EDF3;
    border-radius: 14px;
    margin-bottom: 12px;
}

[data-testid="stExpander"] {
    border: 1px solid #E9EDF3;
    border-radius: 10px;
    background: #FFFFFF;
}

.dm-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 3px 5px 32px;
}

.dm-logo {
    width: 39px;
    height: 39px;
    border-radius: 11px;
    background: #171D2B;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
}

.dm-brand-name {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.12rem;
    font-weight: 800;
    letter-spacing: -.04em;
    color: #171D2B;
}

.dm-brand-sub {
    font-size: .7rem;
    color: #9AA4B5;
}

.dm-nav-label {
    font-size: .67rem;
    font-weight: 800;
    letter-spacing: .12em;
    color: #A1AABB;
    margin: 9px 12px 10px;
}

.dm-eyebrow {
    font-size: .75rem;
    font-weight: 800;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #6366F1;
    margin-bottom: 12px;
}

.dm-description {
    color: #8A94A6;
    font-size: .95rem;
    margin-top: -7px;
    margin-bottom: 26px;
}

.dm-section {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.08rem;
    font-weight: 800;
    letter-spacing: -.025em;
    margin: 24px 0 14px;
    color: #171D2B;
}

.dm-file-title {
    font-weight: 700;
    color: #252D3E;
    overflow-wrap: anywhere;
}

.dm-file-meta {
    color: #94A0B1;
    font-size: .77rem;
    margin-top: 5px;
}

.dm-pill {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 7px;
    font-size: .72rem;
    font-weight: 700;
    background: #F1F3F7;
    color: #687386;
}

.dm-pill.ready {
    background: #E9F7EF;
    color: #228553;
}

.dm-pill.pending {
    background: #FFF5E4;
    color: #A87318;
}

.dm-hero {
    background: #F6F7FF;
    border: 1px solid #ECEEFF;
    border-radius: 16px;
    padding: 28px 30px;
    margin: 14px 0 26px;
}

.dm-hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.2rem;
    font-weight: 800;
    color: #252B49;
    margin-bottom: 8px;
}

.dm-hero-sub {
    color: #7A83A0;
    font-size: .87rem;
    line-height: 1.7;
}

.dm-result-number {
    color: #A1AABB;
    font-size: .78rem;
    font-weight: 800;
}

.dm-sidebar-footer {
    color: #A1AABB;
    font-size: .72rem;
    line-height: 1.9;
}

hr {
    border-color: #EEF0F5 !important;
}

@media (max-width: 900px) {
    .block-container {
        padding: 1.6rem 1rem 3rem;
    }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------
# API
# -----------------------------------------

def esc(value):
    return html.escape(str(value), quote=True)


def api(method, path, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{path}",
            timeout=120,
            **kwargs,
        )
        response.raise_for_status()

        if not response.content:
            return True, None

        return True, response.json()

    except requests.exceptions.RequestException as exc:
        message = str(exc)
        if exc.response is not None:
            try:
                payload = exc.response.json()
                if isinstance(payload, dict):
                    message = payload.get("detail", message)
            except ValueError:
                pass
        st.error(f"Request failed: {message}")
        return False, None

    except ValueError:
        st.error("Invalid JSON response from backend.")
        return False, None


def get_documents():
    ok, result = api("GET", "/documents")
    if not ok:
        return []

    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        return result.get("documents", [])

    return []


def document_choices(docs):
    return {
        f"{d['id']} — {d.get('title', 'Untitled')}": d["id"]
        for d in docs
    }


def heading(label, title, description):
    st.markdown(
        f'<div class="dm-eyebrow">{esc(label)}</div>',
        unsafe_allow_html=True,
    )
    st.title(title)
    st.markdown(
        f'<div class="dm-description">{esc(description)}</div>',
        unsafe_allow_html=True,
    )


def navigate(target):
    st.session_state.page = target
    st.rerun()


def render_sources(sources):
    if not sources:
        st.caption("No sources available.")
        return

    for index, source in enumerate(sources, 1):
        name = source.get("document_title", "Untitled")
        chunk = source.get("chunk_index", "?")
        similarity = source.get("similarity")

        with st.expander(
            f"Source {index} · {name} · Chunk {chunk}"
        ):
            st.caption(
                f"Document #{source.get('document_id', '?')}"
            )
            if isinstance(similarity, (int, float)):
                st.caption(f"Similarity: {similarity:.3f}")

            st.write(source.get("content", ""))


# -----------------------------------------
# SIDEBAR
# -----------------------------------------

with st.sidebar:
    st.markdown("""
    <div class="dm-brand">
        <div class="dm-logo">◈</div>
        <div>
            <div class="dm-brand-name">DocuMind</div>
            <div class="dm-brand-sub">Knowledge Workspace</div>
        </div>
    </div>
    <div class="dm-nav-label">WORKSPACE</div>
    """, unsafe_allow_html=True)

    navigation = [
        ("Overview", "▦  Overview"),
        ("Library", "▤  Document Library"),
        ("Upload", "＋  Upload Document"),
        ("Search", "⌕  Semantic Search"),
        ("Ask AI", "✧  Ask AI"),
    ]

    for key, label in navigation:
        if st.button(
            label,
            key=f"nav_{key}",
            type=(
                "primary"
                if st.session_state.page == key
                else "secondary"
            ),
            use_container_width=True,
        ):
            navigate(key)

    st.divider()

    st.markdown("""
    <div class="dm-nav-label">SYSTEM</div>
    <div class="dm-sidebar-footer" style="padding:0 12px">
        DocuMind v1.0<br>
        FastAPI · PostgreSQL · pgvector<br>
        Gemini · Streamlit
    </div>
    """, unsafe_allow_html=True)


documents = get_documents()
options = document_choices(documents)
page = st.session_state.page

if st.session_state.flash:
    st.success(st.session_state.flash)
    st.session_state.flash = None


# -----------------------------------------
# OVERVIEW
# -----------------------------------------

if page == "Overview":
    heading(
        "Workspace / Overview",
        "Your knowledge, in one place.",
        "A quieter, smarter way to work with your documents.",
    )

    total = len(documents)
    ready = sum(
        str(d.get("status", "")).lower() == "ready"
        for d in documents
    )
    pending = sum(
        str(d.get("status", "")).lower() == "pending"
        for d in documents
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    c1.metric("Total documents", total)
    c2.metric("Ready to explore", ready)
    c3.metric("Pending", pending)

    st.markdown("""
    <div class="dm-hero">
        <div class="dm-eyebrow">INTELLIGENT WORKSPACE</div>
        <div class="dm-hero-title">
            Your documents have more to say.
        </div>
        <div class="dm-hero-sub">
            Search beyond keywords. Ask meaningful questions.
            Turn your uploaded files into an accessible
            knowledge base.
        </div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2, gap="medium")

    with left:
        if st.button(
            "✧  Start asking AI",
            type="primary",
            use_container_width=True,
        ):
            navigate("Ask AI")

    with right:
        if st.button(
            "＋  Add a document",
            use_container_width=True,
        ):
            navigate("Upload")

    st.markdown(
        '<div class="dm-section">Recent documents</div>',
        unsafe_allow_html=True,
    )

    if not documents:
        st.info("No documents yet. Upload your first PDF.")

    for doc in documents[:5]:
        with st.container(border=True):
            left, right = st.columns(
                [5, 1],
                vertical_alignment="center",
            )

            with left:
                st.markdown(
                    f'<div class="dm-file-title">'
                    f'▤ &nbsp; {esc(doc.get("title") or "Untitled")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="dm-file-meta">'
                    f'Document #{esc(doc.get("id"))}'
                    f' · {esc(doc.get("page_count") or "—")} pages'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with right:
                status = str(
                    doc.get("status") or "unknown"
                ).lower()
                css = (
                    status if status in ("ready", "pending")
                    else ""
                )
                st.markdown(
                    f'<span class="dm-pill {css}">'
                    f'{esc(status.title())}</span>',
                    unsafe_allow_html=True,
                )

    if len(documents) > 5:
        if st.button("View all documents →"):
            navigate("Library")


# -----------------------------------------
# LIBRARY
# -----------------------------------------

elif page == "Library":
    heading(
        "Workspace / Library",
        "Document library",
        "Everything you've added to your knowledge base.",
    )

    left, right = st.columns([4, 1])

    with left:
        filter_text = st.text_input(
            "Filter documents",
            placeholder="Search document names...",
            label_visibility="collapsed",
        )

    with right:
        if st.button(
            "＋  New document",
            type="primary",
            use_container_width=True,
        ):
            navigate("Upload")

    filtered = [
        d for d in documents
        if filter_text.lower() in str(
            d.get("title", "")
        ).lower()
    ]

    st.caption(f"{len(filtered)} documents")

    if not filtered:
        st.info("No documents found.")

    for doc in filtered:
        doc_id = doc["id"]
        title = doc.get("title") or "Untitled"
        status = str(doc.get("status") or "unknown").lower()

        with st.container(border=True):
            name_col, status_col, action_col = st.columns(
                [5, 1.4, 1],
                vertical_alignment="center",
            )

            with name_col:
                st.markdown(
                    f'<div class="dm-file-title">'
                    f'▤ &nbsp; {esc(title)}</div>'
                    f'<div class="dm-file-meta">'
                    f'ID {esc(doc_id)} · '
                    f'{esc(doc.get("page_count") or "—")} pages'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with status_col:
                css = (
                    status if status in ("ready", "pending")
                    else ""
                )
                st.markdown(
                    f'<span class="dm-pill {css}">'
                    f'{esc(status.title())}</span>',
                    unsafe_allow_html=True,
                )

            with action_col:
                with st.popover("•••"):
                    st.warning("Deletion is permanent.")
                    st.write(f"Delete **{title}**?")

                    if st.button(
                        "Confirm delete",
                        key=f"delete_{doc_id}",
                        type="primary",
                    ):
                        ok, _ = api(
                            "DELETE",
                            f"/documents/{doc_id}",
                        )
                        if ok:
                            st.session_state.flash = (
                                "Document deleted successfully."
                            )
                            st.rerun()


# -----------------------------------------
# UPLOAD
# -----------------------------------------

elif page == "Upload":
    heading(
        "Workspace / Upload",
        "Bring your documents in.",
        "Turn PDF files into searchable knowledge.",
    )

    left, right = st.columns([3, 1.3], gap="large")

    with left:
        with st.container(border=True):
            st.markdown("### Upload a PDF")
            st.caption(
                "Select a document to extract its text "
                "and generate vector embeddings."
            )

            file = st.file_uploader(
                "Choose your PDF",
                type=["pdf"],
                help="Maximum 10 MB",
            )

            title = st.text_input(
                "Document title",
                placeholder="Optional custom title",
            )

            if file is not None:
                size = file.size / (1024 * 1024)
                st.caption(
                    f"{file.name} · {size:.2f} MB"
                )

                if size > 10:
                    st.error("Maximum file size is 10 MB.")

                elif st.button(
                    "Upload and process →",
                    type="primary",
                    use_container_width=True,
                ):
                    files = {
                        "file": (
                            file.name,
                            file.getvalue(),
                            "application/pdf",
                        )
                    }

                    data = {}
                    if title.strip():
                        data["title"] = title.strip()

                    with st.spinner(
                        "Processing document..."
                    ):
                        ok, result = api(
                            "POST",
                            "/documents/upload",
                            files=files,
                            data=data,
                        )

                    if ok:
                        st.success("Upload successful!")
                        if result is not None:
                            with st.expander(
                                "View processing details"
                            ):
                                st.json(result)

    with right:
        st.markdown("### How it works")
        st.markdown("""
**01 — Upload**

Add a PDF document.

**02 — Extract**

Text is extracted and divided into chunks.

**03 — Embed**

Chunks are converted into vector embeddings.

**04 — Explore**

Search or ask AI questions about your document.
""")
        st.divider()
        st.caption("Supported format: PDF · Maximum 10 MB")


# -----------------------------------------
# SEARCH
# -----------------------------------------

elif page == "Search":
    heading(
        "Workspace / Discover",
        "Find what matters.",
        "Semantic search understands meaning, not just keywords.",
    )

    settings_col, results_col = st.columns(
        [1.2, 2.8],
        gap="large",
    )

    with settings_col:
        st.markdown("### Search settings")

        query = st.text_area(
            "Your query",
            placeholder="What would you like to find?",
            height=120,
        )

        selected = st.selectbox(
            "Search scope",
            ["All documents"] + list(options),
        )

        top_k = st.slider(
            "Results",
            1, 10, 5,
        )

        if st.button(
            "Search →",
            type="primary",
            use_container_width=True,
        ):
            if not query.strip():
                st.warning("Enter a search query.")
            else:
                payload = {
                    "query": query.strip(),
                    "top_k": top_k,
                    "document_id": options.get(selected),
                }

                with st.spinner("Searching..."):
                    ok, result = api(
                        "POST",
                        "/search",
                        json=payload,
                    )

                if ok and isinstance(result, dict):
                    st.session_state.search_results = (
                        result.get("results", [])
                    )

    with results_col:
        st.markdown("### Search results")

        results = st.session_state.search_results

        if results is None:
            st.info(
                "Enter a query to discover relevant "
                "passages from your documents."
            )

        elif not results:
            st.info("No matching passages found.")

        else:
            st.caption(f"{len(results)} results found")

            for index, match in enumerate(results, 1):
                title = match.get(
                    "document_title",
                    "Untitled",
                )
                similarity = match.get("similarity")

                with st.container(border=True):
                    st.markdown(
                        f'<div class="dm-result-number">'
                        f'RESULT {index:02d}</div>'
                        f'<div class="dm-file-title">'
                        f'{esc(title)}</div>',
                        unsafe_allow_html=True,
                    )

                    meta = (
                        f"Document #{match.get('document_id', '?')}"
                        f" · Chunk {match.get('chunk_index', '?')}"
                    )

                    if isinstance(
                        similarity, (float, int)
                    ):
                        meta += (
                            f" · Similarity {similarity:.3f}"
                        )

                    st.caption(meta)
                    st.write(match.get("content", ""))


# -----------------------------------------
# ASK AI
# -----------------------------------------

elif page == "Ask AI":
    heading(
        "Workspace / AI Assistant",
        "Ask DocuMind.",
        "Answers grounded in your own documents.",
    )

    chat_col, settings_col = st.columns(
        [3.2, 1],
        gap="large",
    )

    with settings_col:
        st.markdown("### Context")

        selected = st.selectbox(
            "Document",
            ["All documents"] + list(options),
        )

        top_k = st.slider(
            "Sources",
            1, 10, 5,
            key="ask_top_k",
        )

        st.divider()

        st.caption(
            "DocuMind retrieves relevant passages "
            "before asking Gemini to generate an answer."
        )

        if st.button(
            "Clear conversation",
            use_container_width=True,
        ):
            st.session_state.chat_history = []
            st.rerun()

    with chat_col:
        if not st.session_state.chat_history:
            st.markdown("""
            <div class="dm-hero">
                <div class="dm-eyebrow">YOUR AI RESEARCH ASSISTANT</div>
                <div class="dm-hero-title">
                    What would you like to know?
                </div>
                <div class="dm-hero-sub">
                    Ask a question about your uploaded files.
                    DocuMind will find relevant context and
                    generate a grounded response.
                </div>
            </div>
            """, unsafe_allow_html=True)

        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["question"])

            with st.chat_message(
                "assistant",
                avatar="✦",
            ):
                st.markdown(chat["answer"])

                with st.expander("Sources"):
                    render_sources(chat["sources"])

        question = st.chat_input(
            "Ask your knowledge base..."
        )

        if question:
            payload = {
                "question": question,
                "top_k": top_k,
                "document_id": options.get(selected),
            }

            with st.chat_message("user"):
                st.write(question)

            with st.chat_message(
                "assistant",
                avatar="✦",
            ):
                with st.spinner(
                    "Thinking with your documents..."
                ):
                    ok, result = api(
                        "POST",
                        "/ask",
                        json=payload,
                    )

                if ok and isinstance(result, dict):
                    answer = result.get("answer", "")
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    with st.expander("Sources"):
                        render_sources(sources)

                    st.session_state.chat_history.append({
                        "question": question,
                        "answer": answer,
                        "sources": sources,
                    })
