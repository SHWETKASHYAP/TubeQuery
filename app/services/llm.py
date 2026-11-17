from groq import Groq
from app.config import GROQ_API_KEY, GROQ_MODEL
from app.services.transcript import format_timestamp

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You answer questions about a YouTube video using ONLY the transcript excerpts provided.
Each excerpt begins with its timestamp in square brackets, like [14:32].

Rules:
- If the excerpts do not contain the answer, say you could not find it in this video.
- Cite the timestamps you used in square brackets, like [14:32].
- Be concise."""


def generate_answer(question: str, chunks: list[dict]) -> str:
    context = "\n\n".join(
        f"[{format_timestamp(c['start'])}] {c['text']}" for c in chunks
    )
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.2,
        reasoning_effort="low",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Transcript excerpts:\n{context}\n\nQuestion: {question}",
            },
        ],
    )
    return response.choices[0].message.content