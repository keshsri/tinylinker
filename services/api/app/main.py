from fastapi import FastAPI
from mangum import Mangum

app = FastAPI(title="TinyLinker API")

@app.get("/health")
def health():
    return {"status": "healthy"}

# Lambda handler
handler = Mangum(app)
