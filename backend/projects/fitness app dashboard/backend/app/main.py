
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – fitness_app_dashboard")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "fitness_app_dashboard"}
