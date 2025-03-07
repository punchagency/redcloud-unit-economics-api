import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import base_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="0.0.1",
    description="Nigeria Retail Economics API helps you find marketing opportunities for your products. 🚀",
    swagger_ui_parameters={"syntaxHighlight": False},
    summary="Find marketing opportunities for your products. 🚀",
    terms_of_service="https://whitespace.ai/terms/",
    contact={
        "name": "Nigeria Retail Economics API",
        "url": "https://whitespace.ai/contact/",
        "email": "hello@whitespace.ai",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(base_router, prefix=settings.API_V1_STR)


@app.get("/")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG and settings.ENVIRONMENT.lower() == "development",
    )
