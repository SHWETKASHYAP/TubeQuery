import chromadb
from chromadb.utils import embedding_functions

embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="transcripts",
    embedding_function=embedder,
    metadata={"hnsw:space": "cosine"}
)

def store_chunks(video_id: str, chunks: list[dict]) -> int:
    collection.upsert(
        ids=[f"{video_id}_{c['start']}" for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[{"video_id": video_id, "start": c["start"]} for c in chunks],
    )
    return len(chunks)


def search_chunks(video_id: str, question: str, k: int = 4) -> list[dict]:
    result = collection.query(
        query_texts=[question],
        n_results=k,
        where={"video_id": video_id},  # only this video's chunks
    )
    return [
        {"text": doc, "start": meta["start"], "distance": dist}
        for doc, meta, dist in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        )
    ]
