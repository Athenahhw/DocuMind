
from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import Document, DocumentChunk
from backend.app.chunking import split_text
from backend.app.embeddings import generate_embeddings


def main():
    with SessionLocal() as db:
        documents = db.scalars(
            select(Document)
            .where(Document.content.is_not(None))
        ).all()

        for document in documents:
            existing_chunks = db.scalar(
                select(DocumentChunk.id)
                .where(
                    DocumentChunk.document_id == document.id
                )
                .limit(1)
            )

            if existing_chunks is not None:
                print(
                    f"Skipping document {document.id}: "
                    "chunks already exist"
                )
                continue

            chunks = split_text(document.content)

            if not chunks:
                print(
                    f"Skipping document {document.id}: "
                    "no extractable text"
                )
                continue

            vectors = generate_embeddings(chunks)

            for index, (text, vector) in enumerate(
                zip(chunks, vectors)
            ):
                db.add(
                    DocumentChunk(
                        document_id=document.id,
                        chunk_index=index,
                        content=text,
                        embedding=vector,
                    )
                )

            db.commit()

            print(
                f"Document {document.id}: "
                f"saved {len(chunks)} chunks"
            )


if __name__ == "__main__":
    main()
