from app.services.redis_client import r

VIDEO_TTL_SECONDS = 60 * 60 * 24 * 7  # keep for 7 days


def _key(video_id: str) -> str:
    return f"video:{video_id}"


def get_video(video_id: str) -> dict:
    return r.hgetall(_key(video_id))  # {} if the key doesn't exist


def mark_completed(video_id: str, chunks: int) -> None:
    r.hset(_key(video_id), mapping={"status": "COMPLETED", "chunks": chunks})
    r.expire(_key(video_id), VIDEO_TTL_SECONDS)