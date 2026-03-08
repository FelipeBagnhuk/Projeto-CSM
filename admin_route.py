from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from edit_page import PageStatus
from models import Page, Section, SectionCreate, SectionRead, PageRead, Snapshot 
from data_base import SessionLocal
from sqlalchemy.types import JSON
import json

admin_router = APIRouter(prefix="/admin", tags=["Admin"])  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Função da salvar snapshot

def save_snapshot(entity_id: int, action: str, old_data: dict, db: Session):
    """Salva snapshot dos dados antigos antes da edição"""
    snapshot_data = {
        "entity_id": entity_id,
        "entity_type": old_data.get("entity_type", "section"),  # page ou section
        "old_content": old_data.get("content", old_data),  # Conteúdo antigo
        "old_type": old_data.get("type"),
        "old_order": old_data.get("order")
    }
    
    snapshot = Snapshot(
        entity_id=entity_id,
        entity_type="section" if "content" in old_data else "page",
        action=action,
        data=snapshot_data
    )
    db.add(snapshot)
    db.commit()

#Lista as páginas:

@admin_router.get("/pages", response_model=List[PageRead]) 
async def list_pages(db: Session = Depends(get_db)):
    return db.query(Page).all()

#Criar/editar página (subtitui tudo)

@admin_router.put("/pages/{slug}", response_model=PageRead)  # ← response_model=PageRead
async def update_page(slug: str, page_data: dict, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        page = Page(slug=slug, title=page_data.get("title", ""), status=PageStatus.DRAFT)
        db.add(page)
        db.commit()
        db.refresh(page)
        return page  # ← SQLAlchemy vira PageRead automaticamente
    
    # Atualiza campos
    for key, value in page_data.items():
        if hasattr(page, key):
            setattr(page, key, value)
    
    db.commit()
    db.refresh(page)
    return page

#Lista seções de uma página: 

@admin_router.get("/pages/{slug}/sections", response_model=List[SectionRead])
async def get_page_sections(slug: str, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    
    sections = db.query(Section).filter(Section.page_id == page.id).order_by(Section.order).all()
    return sections

#Atualiza seção específica: 

@admin_router.put("/pages/{slug}/sections/{section_id}", response_model=SectionRead)
async def update_section(slug: str, section_id: int, section_data: SectionCreate, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
        
    section = db.query(Section).filter(Section.id == section_id, Section.page_id == page.id).first()
    if not section:
        raise HTTPException(status_code=404, detail="Seção não encontrada")
    
    # SALVA SNAPSHOT dos dados ANTES da mudança
    old_data = {
        "id": section.id,
        "type": section.type,
        "content": section.content,
        "order": section.order,
        "entity_type": "section"
    }
    save_snapshot(section.id, "section_update", old_data, db)
    
    # Atualiza seção
    section.type = section_data.type
    section.content = section_data.content
    section.order = section_data.order
    
    db.commit()
    db.refresh(section)
    return section

#Reordenar seção

@admin_router.put("/pages/{slug}/sections/reorder")
async def reorder_sections(slug: str, sections_order: List[int], db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    for i, section_id in enumerate(sections_order):
        section = db.query(Section).filter(Section.id == section_id).first()
        if section and section.page_id == page.id:
            section.order = i
    db.commit()
    return {"message": "Ordem atualizada"}

# Publicar página: 

@admin_router.post("/pages/{slug}/publish")
async def publish_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    
    await save_snapshot(page.id, "page_published", page.__dict__.copy(), db)
    page.status = PageStatus.PUBLISHED
    db.commit()
    return {"message": "Página publicada"}

# Previsão (Draft para quem posta, não salva no público)

@admin_router.post("/pages/{slug}/preview")
async def preview_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if page.status != PageStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Só drafts podem ter preview")
    return {"preview_url": f"/preview/{slug}", "page": page}

# Lista Snapshots
@admin_router.get("/snapshots/{entity_id}")
async def list_snapshots(entity_id: int, db: Session = Depends(get_db)):
    # Implementar consulta snapshots
    pass

# 9. Restaura Snapshot

@admin_router.post("/snapshots/{snapshot_id}/restore")
async def restore_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    # Implementar restauração
    pass


