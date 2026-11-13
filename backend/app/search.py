
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Document, DocumentChunk
from .embeddings import generate_embedding


def semantic_search(
    db: Session,
    query: str,
    top_k: int = 5,
    document_id: int | None = None,
) -> list[dict]:

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")

    # Convert the question into a vector
    query_vector = generate_embedding(query)

    # Calculate cosine distance
    distance = DocumentChunk.embedding.cosine_distance(
        query_vector
    )

    # Search relevant document chunks
    statement = (
        select(
            DocumentChunk,
            Document.title.label("document_title"),
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(DocumentChunk.embedding.is_not(None))
    )

    if document_id is not None:
        statement = statement.where(
            DocumentChunk.document_id == document_id
        )

    statement = statement.order_by(distance).limit(top_k)

    rows = db.execute(statement).all()

    results = []

    for chunk, document_title, distance_value in rows:
        results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "document_title": document_title,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity": round(
                1 - float(distance_value),
                4,
            ),
        })

    return results
