# Ingestion

## Input

PDF instruction manuals, dropped into `data/manuals/` (gitignored — local only,
these are copyrighted vendor documents and should not be committed).

## Steps

1. **Load**: extract text per page. Start with `pypdf` (pure Python, no system deps).
   If manuals turn out to be scanned/image-only, revisit with OCR (`pytesseract` or
   `ocrmypdf`) — don't build this until needed.
2. **Chunk**: split page text into overlapping chunks (~500-800 tokens, ~15% overlap)
   to preserve context across boundaries. Keep page number attached to each chunk for
   citation purposes.
3. **Embed**: run chunks through a local embedding model via Ollama
   (e.g. `nomic-embed-text`) — keeps embeddings local, consistent with the rest of
   the stack, no extra Python ML deps needed.
4. **Store**: upsert into `documents` / `chunks` tables in Postgres.

## Idempotency

Re-ingesting the same file should not duplicate chunks — key on
(filename, content hash) or delete-then-reinsert by document_id.

## CLI

```
python -m ragapp.cli ingest <path-to-pdf> [--title "Custom Title"]
python -m ragapp.cli list                  # list ingested documents
python -m ragapp.cli eval [--with-generation]   # see docs/specs/06-evaluation.md
```

`remove <document_id>` is not built yet — re-ingesting the same file (same content
hash) safely upserts rather than duplicating, but there's no way to delete a document
via the CLI today short of `DELETE FROM documents WHERE id = ...` (cascades to its
chunks).
