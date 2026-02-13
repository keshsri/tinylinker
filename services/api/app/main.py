from fastapi import FastAPI
from mangum import Mangum
from app.routers import urls

app = FastAPI(title="TinyLinker API")
app.include_router(urls.router)

@app.get("/health")
def health():
    return {"status": "healthy"}

# Lambda handler
handler = Mangum(app)
