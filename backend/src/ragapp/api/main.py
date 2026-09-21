from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ragapp.llm.client import LLMClient
from ragapp.retrieval.retriever import Retriever
from ragapp.retrieval.store import VectorStore

app = FastAPI(title="rag1")

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


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/documents")
def list_documents():
    return store.list_documents()


@app.post("/api/chat")
def chat(request: ChatRequest):
    results = retriever.retrieve(request.message)
    context = "\n\n".join(
        f"[{doc.filename}, page {chunk.page_number}]\n{chunk.content}" for chunk, doc in results
    )
    sources = [{"filename": doc.filename, "page": chunk.page_number} for chunk, doc in results]

    def event_stream():
        for token in llm_client.chat_stream(request.message, context):
            yield token
        yield f"\n\n[sources: {sources}]"

    return StreamingResponse(event_stream(), media_type="text/plain")
