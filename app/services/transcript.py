from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)

    # Short links: https://youtu.be/VIDEO_ID
    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    # Normal links: https://www.youtube.com/watch?v=VIDEO_ID
    if parsed.hostname in ("www.youtube.com", "youtube.com", "m.youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query)["v"][0]

    raise ValueError("Not a valid YouTube video URL")


def fetch_transcript(video_id: str) -> list[dict]:
    api = YouTubeTranscriptApi()
    fetched = api.fetch(video_id, languages=["en"])
    return fetched.to_raw_data()  # list of {"text", "start", "duration"}


def chunk_transcript(
    snippets: list[dict],
    window_seconds: int = 45,
    overlap_seconds: int = 10,
) -> list[dict]:
    chunks = []
    step = window_seconds - overlap_seconds
    video_end = snippets[-1]["start"] + snippets[-1]["duration"]

    window_start = 0.0
    while window_start < video_end:
        window_end = window_start + window_seconds
        texts = [
            s["text"].replace("\n", " ")
            for s in snippets
            if window_start <= s["start"] < window_end
        ]
        if texts:
            chunks.append({
                "text": " ".join(texts),
                "start": int(window_start),
            })
        window_start += step

    return chunks


def make_timestamp_link(video_id: str, start: int) -> str:
    return f"https://youtube.com/watch?v={video_id}&t={start}s"