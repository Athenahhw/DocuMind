# DocuMind

**An AI-Powered Document Management and Knowledge Base System**

DocuMind is a full-stack AI application that allows users to upload PDF documents, search their contents using semantic similarity, and ask questions through Retrieval-Augmented Generation (RAG).

The system combines document processing, vector embeddings, PostgreSQL vector search, and Google Gemini to generate answers grounded in uploaded documents.

## Features

- **PDF Management:** Upload, process, view, and delete PDF documents.
- **Text Extraction:** Extract text from PDF files using PyMuPDF.
- **Text Chunking:** Split extracted text into overlapping chunks.
- **Vector Embeddings:** Generate semantic embeddings using Sentence Transformers.
- **Semantic Search:** Retrieve relevant document passages using PostgreSQL and pgvector.
- **AI Question Answering:** Generate document-grounded answers using Gemini Flash Lite.
- **Source References:** Display retrieved document chunks alongside AI answers.
- **Web Interface:** Interact with the system through Streamlit.
- **Chat History:** Review questions and answers during the current browser session.

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Frontend | Streamlit |
| Database | PostgreSQL |
| Vector Database | pgvector |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM | Google Gemini Flash Lite |
| PDF Processing | PyMuPDF |
| Testing | Pytest |

## System Architecture

```text
User
 |
 v
Streamlit Frontend
 |
 v
FastAPI Backend
 |
 +-- PDF Upload
 |     |
 |     v
 |   PyMuPDF
 |     |
 |     v
 |   Text Chunking
 |     |
 |     v
 |   Sentence Transformers
 |     |
 |     v
 |   PostgreSQL + pgvector
 |
 +-- User Question
       |
       v
    Embedding Model
       |
       v
    Vector Similarity Search
       |
       v
    Relevant Document Chunks
       |
       v
    Google Gemini API
       |
       v
    Answer + Source References
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Athenahhw/DocuMind.git
cd DocuMind
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```dotenv
DATABASE_URL=postgresql+psycopg://localhost/documind
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Never commit your actual API keys to GitHub.

### 5. Set up PostgreSQL

Create a PostgreSQL database named `documind`, enable the `vector` extension, and apply the project's database schema.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 6. Start the backend

```bash
python -m uvicorn backend.app.main:app --reload
```

API documentation:

`http://127.0.0.1:8000/docs`

### 7. Start the frontend

Open another terminal:

```bash
python -m streamlit run frontend/app.py
```

Web interface:

`http://localhost:8501`

## Running Tests

```bash
python -m pytest tests/ -v
```

The test suite includes unit tests for text chunking and semantic search, along with basic FastAPI smoke tests.

## Screenshots

Add screenshots of the following features:

- Dashboard
- PDF Upload
- Semantic Search
- AI Question Answering

## Current Limitations

- Only PDF documents are supported.
- Text extraction may not work for scanned PDFs without OCR.
- Chat history is stored only in the current Streamlit session.
- Source references identify document chunks rather than exact PDF pages.
- Semantic search relevance depends on the embedding model and similarity threshold.

## Future Improvements

- Improve the web interface and user experience.
- Add page-level source citations.
- Support additional document formats.
- Add persistent conversation history.
- Containerize the application with Docker.
- Deploy an online demo.

## Author

Developed by [Athenahhw](https://github.com/Athenahhw).
