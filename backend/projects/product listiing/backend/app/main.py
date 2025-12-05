
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – product_listiing")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "product_listiing"}
