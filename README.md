# DocuMind

**AI-Powered Document Management & Knowledge Base**

DocuMind is a full-stack AI application that transforms PDF documents into a searchable knowledge base. Users can upload documents, perform semantic search, and ask natural-language questions through a Retrieval-Augmented Generation (RAG) pipeline.

The project combines document processing, vector embeddings, PostgreSQL, and the Google Gemini API in a containerized application.

## Features

- **PDF Management:** Upload, view, and delete PDF documents.
- **Text Extraction:** Automatically extract text from uploaded PDFs using PyMuPDF.
- **Document Chunking:** Split extracted content into smaller, overlapping passages.
- **Vector Embeddings:** Generate 384-dimensional embeddings using Sentence Transformers.
- **Semantic Search:** Retrieve relevant document passages using cosine similarity and pgvector.
- **AI Question Answering:** Generate answers grounded in retrieved passages using Google Gemini.
- **Source References:** Display supporting document passages alongside AI-generated answers.
- **Docker Support:** Run the frontend, backend, and PostgreSQL database using Docker Compose.
- **Automated Testing:** Validate core application functionality with Pytest.

## Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | PostgreSQL |
| Vector Database | pgvector |
| PDF Processing | PyMuPDF |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| LLM | Google Gemini API |
| Containerization | Docker, Docker Compose |
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
          +---------+----------+
          |                    |
          v                    v
     PDF Processing       RAG Pipeline
          |                    |
          v                    v
    Text Extraction      Semantic Search
          |                    |
          v                    v
       Chunking          Relevant Chunks
          |                    |
          v                    v
   Vector Embeddings      Gemini API
          |                    |
          +---------+----------+
                    |
                    v
          PostgreSQL + pgvector
```

## Application Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

Manage uploaded documents and monitor processing status.

### PDF Upload

![PDF Upload](docs/screenshots/upload.png)

Upload PDF documents for automatic text extraction, chunking, and embedding generation.

### Semantic Search

![Semantic Search](docs/screenshots/semantic-search.png)

Find relevant document passages using vector similarity search.

### AI Question Answering

![Ask AI](docs/screenshots/ask-ai.png)

Ask questions about uploaded documents and receive AI-generated answers with source references.

## Getting Started

### Prerequisites

- Docker Desktop
- Docker Compose
- Google Gemini API key

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/Athenahhw/DocuMind.git
cd DocuMind
```

**2. Configure environment variables**

```bash
cp .env.example .env
```

Update `.env` with your Gemini API key, supported Gemini model, and PostgreSQL password.

**3. Build and start the application**

```bash
docker compose up -d --build
```

**4. Access the application**

- Frontend: http://localhost:8501
- FastAPI documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

**5. Stop the application**

```bash
docker compose down
```

Docker volumes preserve the database and uploaded files between ordinary restarts.

**Database initialization:** The PostgreSQL service must initialize the schema in `database/init.sql` on first startup.

## Testing

Run the automated tests from the project root:

```bash
python -m pytest tests/ -v
```

The test suite covers text chunking, semantic search behavior, and API endpoint registration.

## How RAG Works

1. A user uploads a PDF document.
2. PyMuPDF extracts the text.
3. The text is split into overlapping chunks.
4. Sentence Transformers generates embeddings for each chunk.
5. PostgreSQL stores the document, chunks, and vectors.
6. A user submits a natural-language question.
7. The question is converted into an embedding.
8. pgvector retrieves semantically relevant chunks.
9. Retrieved passages are provided as context to Gemini.
10. Gemini generates an answer with supporting source references.

## Limitations

- The current version is designed primarily for local, single-user use.
- A publicly hosted demo is not currently available.
- Scanned PDFs may require OCR before their text can be processed.
- AI-generated answers may contain inaccuracies.
- Authentication and multi-user document isolation have not yet been implemented.

## Future Improvements

- User authentication and access control
- Multi-user document management
- OCR support for scanned PDFs
- Hybrid keyword and vector search
- Improved retrieval evaluation
- Cloud deployment

## Author

**Athena Wang**

Computer Science Undergraduate

[GitHub](https://github.com/Athenahhw/DocuMind)
