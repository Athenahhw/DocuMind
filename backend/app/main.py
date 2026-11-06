from pathlib import Path
from uuid import uuid4
from .pdf_processor import extract_pdf_text
from .schemas import DocumentContentResponse
from fastapi import File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .database import get_db
from .models import Document
from .schemas import DocumentCreate, DocumentResponse


app = FastAPI(
    title="DocuMind API",
    version="0.2.0"
)
BASE_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

@app.get("/")
def home():
    return {"message": "Welcome to DocuMind!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=201
)
def create_document(
    data: DocumentCreate,
    db: Session = Depends(get_db)
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
            detail="Invalid document data or category ID"
        )

    return document


@app.get(
    "/documents",
    response_model=list[DocumentResponse]
)
def list_documents(
    db: Session = Depends(get_db)
):
    statement = select(Document).order_by(Document.id)
    return db.scalars(statement).all()


@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document



@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = Path(document.file_path)
    upload_root = UPLOAD_DIR.resolve()
    resolved_path = file_path.resolve()

    # 先刪除資料庫紀錄
    db.delete(document)
    db.commit()

    # 只清理 uploads 內的檔案
    if resolved_path.is_relative_to(upload_root):
        resolved_path.unlink(missing_ok=True)

    return {
        "message": "Document deleted successfully"
    }
@app.post(
    "/documents/upload",
    response_model=DocumentResponse,
    status_code=201
)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    category_id: int | None = Form(None),
    db: Session = Depends(get_db)
):
    # 1. 檢查副檔名
    original_name = Path(file.filename or "").name

    if Path(original_name).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2. 讀取檔案，限制最大 10 MB
    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 10 MB"
        )

    # 3. 基本 PDF 格式檢查
    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF file"
        )

    # 4. 產生唯一檔名，避免覆蓋
    unique_filename = f"{uuid4().hex}.pdf"
    saved_path = UPLOAD_DIR / unique_filename

    try:
        # 5. 儲存實體 PDF
        saved_path.write_bytes(content)
        pdf_data = extract_pdf_text(str(saved_path))
        # 6. 建立資料庫紀錄
        document = Document(
            title=title,
            filename=original_name,
            file_path=str(saved_path),
            file_type="pdf",
            category_id=category_id,
            status="ready",
            content=pdf_data["content"],
            page_count=pdf_data["page_count"]
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        # 如果資料庫寫入失敗，清理檔案
        saved_path.unlink(missing_ok=True)
        raise

    finally:
        await file.close()

@app.get("/documents/{document_id}/download")
def download_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    file_path = Path(document.file_path)

    # 確認檔案位於 uploads 目錄內
    if not file_path.resolve().is_relative_to(
        UPLOAD_DIR.resolve()
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path"
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found"
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=document.filename
    )

@app.get(
    "/documents/{document_id}/content",
    response_model=DocumentContentResponse
)
def get_document_content(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document
