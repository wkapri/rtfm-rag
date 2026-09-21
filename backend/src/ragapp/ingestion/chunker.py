from ragapp.models import Chunk


def chunk_pages(pages: list[str], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """Split page text into overlapping chunks, preserving page number per chunk.

    chunk_size/chunk_overlap are in characters (simple and dependency-free);
    swap for a token-aware splitter later if chunk boundaries prove noisy.
    """
    chunks: list[Chunk] = []
    chunk_index = 0
    step = max(chunk_size - chunk_overlap, 1)

    for page_number, text in enumerate(pages, start=1):
        text = text.strip()
        if not text:
            continue
        for start in range(0, len(text), step):
            piece = text[start : start + chunk_size].strip()
            if not piece:
                continue
            chunks.append(Chunk(content=piece, page_number=page_number, chunk_index=chunk_index))
            chunk_index += 1
            if start + chunk_size >= len(text):
                break

    return chunks
