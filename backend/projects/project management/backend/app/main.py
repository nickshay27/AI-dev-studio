
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – Project Management")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Project Management"}
