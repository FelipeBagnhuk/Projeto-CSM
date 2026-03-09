from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Page, Section
from data_base import SessionLocal

public_router = APIRouter(prefix="/public", tags=["Public"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ROTA PÚBLICA - VISUALIZAÇÃO 
@public_router.get("/pages/{slug}")
def get_page_sections(slug: str, db: Session = Depends(get_db)):
    # ✅ SQLAlchemy 1.x - SEM ERROS
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    
    # ✅ Mesma sintaxe 1.x - SEM ERROS
    sections = db.query(Section).filter(Section.page_id == page.id).order_by(Section.order).all()
    
    return {
        "page": page.__dict__,
        "sections": [s.__dict__ for s in sections]
    }
