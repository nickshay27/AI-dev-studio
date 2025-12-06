
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – scrap")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "scrap"}
