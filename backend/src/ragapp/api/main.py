import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ragapp.eval.heuristics import extract_citations, is_refusal
from ragapp.llm.client import LLMClient
from ragapp.retrieval.retriever import Retriever
from ragapp.retrieval.store import VectorStore, init_schema

app = FastAPI(title="rag1")
init_schema()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = Retriever()
llm_client = LLMClient()
store = VectorStore()


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    filename: str
    page: int


class RetrievedChunk(BaseModel):
    rank: int
    filename: str
    page: int
    preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    query_log_id: str
    refused: bool
    retrieval_latency_ms: int
    embed_latency_ms: int
    search_latency_ms: int
    generation_latency_ms: int
    retrieved_chunks: list[RetrievedChunk]


class FeedbackRequest(BaseModel):
    feedback: int  # 1 = thumbs up, -1 = thumbs down


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/documents")
def list_documents():
    return store.list_documents()


@app.get("/api/logs")
def list_logs(limit: int = 20):
    return store.list_query_logs(limit)


@app.get("/api/stats")
def stats():
    return store.get_stats()


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    retrieval_start = time.monotonic()
    retrieval = retriever.retrieve_with_timing(request.message)
    results = retrieval.results
    retrieval_latency_ms = int((time.monotonic() - retrieval_start) * 1000)

    context = "\n\n".join(
        f"[{doc.filename}, page {chunk.page_number}]\n{chunk.content}" for chunk, doc in results
    )

    generation_start = time.monotonic()
    answer = "".join(llm_client.chat_stream(request.message, context))
    generation_latency_ms = int((time.monotonic() - generation_start) * 1000)

    seen: set[tuple[str, int]] = set()
    sources = []
    for chunk, doc in results:
        key = (doc.filename, chunk.page_number)
        if key not in seen:
            seen.add(key)
            sources.append(Source(filename=doc.filename, page=chunk.page_number))

    retrieved_chunks = [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "filename": doc.filename,
            "page": chunk.page_number,
            "rank": rank,
        }
        for rank, (chunk, doc) in enumerate(results)
    ]
    refused = is_refusal(answer)
    cited_sources = extract_citations(answer, results)

    query_log_id = store.log_query(
        question=request.message,
        answer=answer,
        retrieved_chunks=retrieved_chunks,
        cited_sources=cited_sources,
        refused=refused,
        retrieval_latency_ms=retrieval_latency_ms,
        embed_latency_ms=retrieval.embed_latency_ms,
        search_latency_ms=retrieval.search_latency_ms,
        generation_latency_ms=generation_latency_ms,
    )

    return ChatResponse(
        answer=answer,
        sources=sources,
        query_log_id=query_log_id,
        refused=refused,
        retrieval_latency_ms=retrieval_latency_ms,
        embed_latency_ms=retrieval.embed_latency_ms,
        search_latency_ms=retrieval.search_latency_ms,
        generation_latency_ms=generation_latency_ms,
        retrieved_chunks=[
            RetrievedChunk(rank=rank, filename=doc.filename, page=chunk.page_number, preview=chunk.content[:160])
            for rank, (chunk, doc) in enumerate(results)
        ],
    )


@app.post("/api/feedback/{query_log_id}")
def feedback(query_log_id: str, request: FeedbackRequest):
    if request.feedback not in (1, -1):
        raise HTTPException(status_code=400, detail="feedback must be 1 or -1")
    store.set_feedback(query_log_id, request.feedback)
    return {"status": "ok"}
