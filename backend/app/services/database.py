from sqlalchemy import text
from sqlalchemy.orm import Session


def check_database_connection(db: Session) -> bool:
    db.execute(text("SELECT 1"))
    return True
