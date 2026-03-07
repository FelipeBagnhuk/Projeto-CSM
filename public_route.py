from fastapi import APIRouter, FastAPI, Depends
from sqlalchemy.orm import Session
from edit_page import Page, SessionLocal

admin_router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ROTA PÚBLICA - VISUALIZAÇÃO
@app.get("/public")
def public_view(db: Session = Depends(get_db)):
    pages = db.scalars(db.select(Page)).all()
    return {"pages": [page.__dict__ for page in pages]}