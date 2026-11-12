from .search import semantic_search
from .rag import answer_question
from pathlib import Path
from uuid import uuid4
from .embeddings import generate_embeddings
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .rag import answer_question
from .database import get_db
from .models import Document, DocumentChunk
from .schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentContentResponse,
    DocumentChunkResponse,
    SearchRequest,
    SearchResponse,
    AskRequest,
    AskResponse,
)
from .pdf_processor import extract_pdf_text
from .chunking import split_text


# ==========================================
# 1. FastAPI configuration
# ==========================================

app = FastAPI(
    title="DocuMind API",
    description="AI-powered document management system",
    version="0.6.0",
)

BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# ==========================================
# 2. Basic API
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to DocuMind!",
        "version": "0.6.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ==========================================
# 3. Create document metadata
# ==========================================

@app.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=201,
)
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db),
):
    document = Document(**data.model_dump())

    db.add(document)

    try:
        db.commit()
        db.refresh(document)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Invalid document data or category ID",
        )

    return document


# ==========================================
# 4. List documents
# ==========================================

@app.get(
    "/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
):
    statement = select(Document).order_by(Document.id)

    return db.scalars(statement).all()


# ==========================================
# 5. Upload PDF + extract text + chunking
# ==========================================

@app.post(
    "/documents/upload",
    response_model=DocumentResponse,
    status_code=201,
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category_id: int | None = Form(None),
    db: Session = Depends(get_db),
):
    original_name = Path(file.filename or "").name

    # Validate filename
    if Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    # Read file with size limit
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB",
        )

    # Basic PDF signature validation
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file",
        )

    # Generate unique filename
    unique_filename = f"{uuid4().hex}.pdf"
    saved_path = UPLOAD_DIR / unique_filename

    try:
        # Save PDF to disk
        saved_path.write_bytes(content)

        # Extract PDF text
        pdf_data = extract_pdf_text(str(saved_path))

        # Split extracted text into chunks
        chunks = split_text(pdf_data["content"])
        embeddings = generate_embeddings(chunks)
        # Create document record
        document = Document(
            title=title,
            filename=original_name,
            file_path=str(saved_path),
            file_type="pdf",
            category_id=category_id,
            status="ready",
            content=pdf_data["content"],
            page_count=pdf_data["page_count"],
        )

        db.add(document)

        # Generate document ID
        db.flush()

        # Create chunks
        
        for index, (chunk_text, vector) in enumerate(
            zip(chunks, embeddings)
        ):
            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk_text,
                embedding=vector,
            )
            db.add(chunk)


        # Commit document and chunks together
        db.commit()
        db.refresh(document)

        return document

    except IntegrityError:
        db.rollback()
        saved_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="Invalid category ID or document data",
        )

    except Exception:
        db.rollback()
        saved_path.unlink(missing_ok=True)
        raise

    finally:
        await file.close()


# ==========================================
# 6. Get document by ID
# ==========================================

@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


# ==========================================
# 7. Get extracted PDF content
# ==========================================

@app.get(
    "/documents/{document_id}/content",
    response_model=DocumentContentResponse,
)
def get_document_content(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    return document


# ==========================================
# 8. Get document chunks
# ==========================================

@app.get(
    "/documents/{document_id}/chunks",
    response_model=list[DocumentChunkResponse],
)
def get_document_chunks(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    statement = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )

    return db.scalars(statement).all()


# ==========================================
# 9. Download PDF
# ==========================================

@app.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(document.file_path).resolve()

    # Prevent access outside uploads directory
    if not file_path.is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=document.filename,
    )


# ==========================================
# 10. Delete document and stored PDF
# ==========================================

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    file_path = Path(document.file_path).resolve()

    db.delete(document)
    db.commit()

    # Only delete files inside uploads
    if file_path.is_relative_to(UPLOAD_DIR.resolve()):
        file_path.unlink(missing_ok=True)

    return {
        "message": "Document deleted successfully"
    }


@app.post("/search", response_model=SearchResponse)
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty",
        )

    if not 1 <= request.top_k <= 20:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20",
        )

    if request.document_id is not None:
        document = db.get(Document, request.document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

    results = semantic_search(
        db=db,
        query=request.query,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    return {
        "query": request.query,
        "total_results": len(results),
        "results": results,
    }



@app.post("/ask", response_model=AskResponse)
def ask_document(
    request: AskRequest,
    db: Session = Depends(get_db),
):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    if not 1 <= request.top_k <= 20:
        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20",
        )

    if request.document_id is not None:
        document = db.get(Document, request.document_id)

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )

    try:
        return answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k,
            document_id=request.document_id,
        )
    except Exception:
        import logging
        logging.exception("RAG request failed")
        raise HTTPException(
            status_code=502,
            detail="AI answer generation failed. Check server logs.",
        )
