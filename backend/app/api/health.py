from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.database import check_database_connection

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app": "QuoteFlow Pro",
    }


@router.get("/database")
def database_health_check(db: Session = Depends(get_db)) -> dict[str, str]:
    check_database_connection(db)

    return {
        "status": "ok",
        "database": "connected",
    }
