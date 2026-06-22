from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.companies import router as companies_router
from app.api.customers import router as customers_router
from app.api.health import router as health_router
from app.api.products import router as products_router
from app.api.quotes import router as quotes_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "QuoteFlow Pro API is running",
        "environment": settings.app_env,
    }


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(companies_router)
app.include_router(customers_router)
app.include_router(products_router)
app.include_router(quotes_router)
