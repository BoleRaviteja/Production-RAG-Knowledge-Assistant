from app.services.chunking import chunk_text


def test_empty():
    assert chunk_text("   \n\n ") == []


def test_small_text_single_chunk():
    assert chunk_text("Hello world.", 100, 10) == ["Hello world."]


def test_chunks_respect_size():
    text = "\n\n".join(f"Paragraph {i}. " + "word " * 60 for i in range(20))
    chunks = chunk_text(text, size=500, overlap=80)
    assert len(chunks) > 1
    assert all(len(c) <= 500 for c in chunks)


def test_overlap_is_present():
    text = "\n\n".join(f"Section {i} " + "lorem ipsum " * 30 for i in range(6))
    chunks = chunk_text(text, size=500, overlap=100)
    tail = chunks[0][-40:].strip()
    assert tail.split()[-1] in chunks[1][:200]


def test_long_text_without_punctuation():
    chunks = chunk_text("x" * 2500, size=1000, overlap=0)
    assert [len(c) for c in chunks] == [1000, 1000, 500]
