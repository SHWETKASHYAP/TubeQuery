from fastapi import FastAPI

app = FastAPI(title="TubeQuery")

@app.get("/health")
def health():
    return {"status": "ok"}