
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – gym_dashboard")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gym_dashboard"}
