# Retrieval

## Similarity search

- Embed the user's query with the same embedding model used at ingestion time.
- Cosine similarity search against `chunks.embedding` via pgvector (`<=>` operator).
- Return top-k (default k=5) chunks, each with document filename + page number.

## Prompt construction

System prompt instructs the LLM to:
- Answer only from the provided excerpts.
- Cite source (filename + page) for claims.
- Say it doesn't know if the excerpts don't cover the question, rather than
  guessing from general knowledge.

## Future improvements (not built yet)

- Hybrid search (keyword + vector) for exact terms like error codes/model numbers.
- Re-ranking retrieved chunks before sending to the LLM.
- Filtering retrieval by document (e.g. "just search the dishwasher manual").
