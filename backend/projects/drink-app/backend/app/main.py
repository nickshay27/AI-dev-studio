
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – drink-app")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "drink-app"}
