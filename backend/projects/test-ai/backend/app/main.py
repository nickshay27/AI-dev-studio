from fastapi import FastAPI

app = FastAPI(title="AI Generated Backend – test-ai")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "test-ai"}  # type: ignore

# TODO:
# - Implement real domain models and routes according to the project plan.
# - Add auth, business logic, and persistence.
