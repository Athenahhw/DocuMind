
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

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}
