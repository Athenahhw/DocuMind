
from sqlalchemy import select

from backend.app.database import SessionLocal
from backend.app.models import DocumentChunk
from backend.app.embeddings import generate_embeddings


BATCH_SIZE = 16


def main():
    with SessionLocal() as db:
        chunks = db.scalars(
            select(DocumentChunk)
            .where(DocumentChunk.embedding.is_(None))
            .order_by(DocumentChunk.id)
        ).all()

        print(f"Chunks without embeddings: {len(chunks)}")

        for start in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[start:start + BATCH_SIZE]

            vectors = generate_embeddings(
                [chunk.content for chunk in batch]
            )

            for chunk, vector in zip(batch, vectors):
                chunk.embedding = vector

            db.commit()

            print(
                f"Processed {min(start + BATCH_SIZE, len(chunks))}"
                f"/{len(chunks)} chunks"
            )


if __name__ == "__main__":
    main()
