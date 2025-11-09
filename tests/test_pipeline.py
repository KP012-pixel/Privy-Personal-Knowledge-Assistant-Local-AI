import tempfile
from backend.ingestion import _smart_chunk

def test_smart_chunk_simple():
    text = "This is a short paragraph. It should remain as one chunk."
    chunks = _smart_chunk(text)
    assert len(chunks) == 1

def test_smart_chunk_list():
    text = "1) First item\n2) Second item\n3) Third item"
    chunks = _smart_chunk(text)
    assert len(chunks) >= 3
