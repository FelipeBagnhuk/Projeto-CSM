from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Page, Section
from data_base import SessionLocal


public_router = APIRouter(prefix="/public", tags=["Public"])  # Mudança aqui

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ROTA PÚBLICA - VISUALIZAÇÃO #Aprimorar rota futuramente
@public_router.get("/pages/{slug}")
def get_page_sections(slug: str, db: Session = Depends(get_db)):
    page = db.scalar(db.select(Page).where(Page.slug == slug))
    if not page:
        raise HTTPException(404, "Página não encontrada")
    
    sections = db.scalars(
        db.select(Section).where(Section.page_id == page.id).order_by(Section.order)
    ).all()
    
    return {
        "page": page.__dict__,
        "sections": [s.__dict__ for s in sections]
    }

