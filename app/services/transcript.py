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