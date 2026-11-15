
import pytest

from backend.app.chunking import split_text


def test_empty_text():
    assert split_text("") == []


def test_short_text():
    result = split_text(
        "Hello DocuMind",
        chunk_size=100,
        overlap=20,
    )

    assert result == ["Hello DocuMind"]


def test_long_text():
    text = "A" * 1200

    result = split_text(
        text,
        chunk_size=500,
        overlap=100,
    )

    assert len(result) == 3
    assert len(result[0]) == 500
    assert len(result[1]) == 500
    assert len(result[2]) == 400


def test_overlap():
    text = "ABCDEFGHIJ"

    result = split_text(
        text,
        chunk_size=6,
        overlap=2,
    )

    assert result == [
        "ABCDEF",
        "EFGHIJ",
    ]


def test_invalid_chunk_size():
    with pytest.raises(ValueError):
        split_text(
            "Hello",
            chunk_size=0,
        )


def test_invalid_overlap():
    with pytest.raises(ValueError):
        split_text(
            "Hello",
            chunk_size=100,
            overlap=100,
        )
