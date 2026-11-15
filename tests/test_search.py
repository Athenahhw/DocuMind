
from unittest.mock import MagicMock, patch

import pytest

from backend.app.search import semantic_search


def test_empty_search_query():
    db = MagicMock()

    with pytest.raises(ValueError):
        semantic_search(
            db=db,
            query="   ",
        )


def test_invalid_top_k():
    db = MagicMock()

    with pytest.raises(ValueError):
        semantic_search(
            db=db,
            query="Python",
            top_k=0,
        )


@patch("backend.app.search.generate_embedding")
def test_search_no_results(mock_embedding):
    mock_embedding.return_value = [0.1] * 384

    db = MagicMock()
    db.execute.return_value.all.return_value = []

    results = semantic_search(
        db=db,
        query="What is Python?",
        top_k=5,
    )

    assert results == []
    mock_embedding.assert_called_once_with(
        "What is Python?"
    )


@patch("backend.app.search.generate_embedding")
def test_search_returns_results(mock_embedding):
    mock_embedding.return_value = [0.1] * 384

    chunk = MagicMock()
    chunk.id = 10
    chunk.document_id = 6
    chunk.chunk_index = 2
    chunk.content = "Python strings store text."

    db = MagicMock()
    db.execute.return_value.all.return_value = [
        (chunk, "string", 0.2)
    ]

    results = semantic_search(
        db=db,
        query="What is a string?",
        top_k=5,
    )

    assert len(results) == 1
    assert results[0]["document_id"] == 6
    assert results[0]["chunk_index"] == 2
    assert results[0]["similarity"] == 0.8
