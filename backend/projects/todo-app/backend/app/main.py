
from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – todo-app")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "todo-app"}
