
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – simple Tv dashboard")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "simple Tv dashboard"}
