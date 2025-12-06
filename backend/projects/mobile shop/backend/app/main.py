
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – mobile_shop")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "mobile_shop"}
