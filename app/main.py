from fastapi import FastAPI, HTTPException
from app.schemas import (
    IngestRequest, IngestResponse, AskRequest, AskResponse, Source,
)
from app.services.transcript import (
    extract_video_id, fetch_transcript, chunk_transcript,
    make_timestamp_link, format_timestamp,
)
from app.services.vector_store import store_chunks, search_chunks
from app.services.llm import generate_answer

app = FastAPI(title="TubeQuery")

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/videos/ingest", response_model=IngestResponse)
def ingest(req: IngestRequest):
    try:
        video_id = extract_video_id(req.url)
    except (ValueError, KeyError):
        raise HTTPException(status_code=400, detail="Not a valid YouTube video URL")

    try:
        snippets = fetch_transcript(video_id)
    except Exception:
        raise HTTPException(
            status_code=422,
            detail="Could not fetch a transcript (no captions, or YouTube blocked the request)",
        )

    chunks = chunk_transcript(snippets)
    stored = store_chunks(video_id, chunks)
    return IngestResponse(video_id=video_id, chunks_stored=stored)


@app.post("/api/v1/videos/ask", response_model=AskResponse)
def ask(req: AskRequest):
    chunks = search_chunks(req.video_id, req.question, k=4)
    if not chunks:
        raise HTTPException(status_code=404, detail="Video not ingested yet")

    answer = generate_answer(req.question, chunks)
    sources = [
        Source(
            timestamp=format_timestamp(c["start"]),
            url=make_timestamp_link(req.video_id, c["start"]),
            text=c["text"],
        )
        for c in chunks
    ]
    return AskResponse(answer=answer, sources=sources)