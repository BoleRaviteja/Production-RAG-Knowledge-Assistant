import re


def chunk_text(text: str, size: int = 1000, overlap: int = 150) -> list[str]:
    """Paragraph-aware chunker with character overlap.

    1. Split on blank lines (keeps paragraphs/sections together).
    2. Paragraphs longer than `size` are split on sentence boundaries, then hard-cut.
    3. Units are greedily packed up to `size`; each new chunk starts with the tail
       of the previous one so facts split across a boundary are still retrievable.
    """
    text = re.sub(r"[ \t]+", " ", text).strip()
    if not text:
        return []

    units: list[str] = []
    for para in (p.strip() for p in re.split(r"\n\s*\n", text)):
        if not para:
            continue
        units.extend([para] if len(para) <= size else _split_long(para, size))

    chunks: list[str] = []
    current = ""
    for unit in units:
        if not current:
            current = unit
        elif len(current) + 2 + len(unit) <= size:
            current += "\n\n" + unit
        else:
            chunks.append(current)
            tail = _overlap_tail(current, overlap)
            current = f"{tail}\n\n{unit}" if tail and len(tail) + 2 + len(unit) <= size else unit
    if current:
        chunks.append(current)
    return chunks


def _split_long(paragraph: str, size: int) -> list[str]:
    parts: list[str] = []
    buf = ""
    for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
        while len(sentence) > size:  # pathological: no punctuation
            if buf:
                parts.append(buf)
                buf = ""
            parts.append(sentence[:size])
            sentence = sentence[size:]
        if not buf:
            buf = sentence
        elif len(buf) + 1 + len(sentence) <= size:
            buf += " " + sentence
        else:
            parts.append(buf)
            buf = sentence
    if buf:
        parts.append(buf)
    return parts


def _overlap_tail(chunk: str, overlap: int) -> str:
    if overlap <= 0:
        return ""
    tail = chunk[-overlap:]
    i = tail.find(" ")
    return tail[i + 1 :] if i != -1 else tail
