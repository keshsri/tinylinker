from fastapi import FastAPI
from mangum import Mangum
import os
from app.routers import urls

# Set root_path dynamically for Lambda
root_path = ""
if os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
    root_path = f"/{os.environ.get('API_GATEWAY_STAGE', 'dev')}"

app = FastAPI(
    title="TinyLinker API",
    root_path=root_path,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(urls.router)

@app.get("/health")
def health():
    return {"status": "healthy"}

# Lambda handler
handler = Mangum(app, lifespan="off")
