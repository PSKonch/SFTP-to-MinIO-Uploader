from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="SFTP to MinIO Uploader",
    version="1.0.0",
    description="A FastAPI application for uploading files from SFTP to MinIO",
    lifespan=lifespan
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)