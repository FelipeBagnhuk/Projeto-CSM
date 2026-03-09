from typing import List, Optional, cast, Any 
from models import Page, Section, SectionCreate, SectionRead, PageRead, Snapshot 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from edit_page import PageStatus
from models import Page, Section, SectionCreate, SectionRead, PageRead, Snapshot 
from data_base import SessionLocal
from sqlalchemy.types import JSON
import json
from typing import Optional

admin_router = APIRouter(prefix="/admin", tags=["Admin"])  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Função da salvar snapshot

def save_snapshot(entity_id: str | int, action: str, snapshot_data: dict, db: Session):
    """Salva snapshot dos dados antigos antes da edição"""
    snapshot = Snapshot(
        entity_id=str(entity_id),  # Converte tudo pra string
        entity_type=snapshot_data["entity_type"],
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
async def update_section(slug: str, section_data: SectionCreate, section_id: int, db: Session = Depends(get_db)):
    # Busca page e section
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    
    section_query = db.query(Section).filter(Section.id == section_id, Section.page_id == page.id)
    section = section_query.first()
    if not section:
        raise HTTPException(status_code=404, detail="Seção não encontrada")

    # SNAPSHOT SEM ERROS - usa query direta
    snapshot_data = {
        "entity_id": section_id, 
        "entity_type": "section",
        "old_type": section.type or "",
        "old_content": section.content or "",
        "old_order": section.order or 0
    }
    save_snapshot(section_id, "section_update", snapshot_data, db)

    update_dict = section_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(section, key, value)

    db.commit()
    db.refresh(section)
    return section

#Reordenar seção

@admin_router.put("/pages/{slug}/sections/reorder")
async def reorder_sections(slug: str, sections_order: List[int], db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    
    for i, section_id in enumerate(sections_order):
        section_query = db.query(Section).filter(Section.id == section_id, Section.page_id == page.id)
        section = section_query.first()
        
        if section is not None: 
            setattr(section, 'order', i)  
    
    db.commit()
    return {"message": "Ordem atualizada"}

# Publicar página: 

@admin_router.post("/pages/{slug}/publish")
async def publish_page(slug: str, db: Session = Depends(get_db)):
    # Busca page SEM type hint problemático
    page_query = db.query(Page).filter(Page.slug == slug)
    page = page_query.first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    

    page_snapshot = {
        "entity_id": slug,  # ← Usa STRING slug ao invés de page.id
        "entity_type": "page",
        "old_status": getattr(page, 'status', 'draft'),
        "old_title": getattr(page, 'title', ''),
        "old_slug": getattr(page, 'slug', '')
    }
    
    save_snapshot(slug, "page_published", page_snapshot, db)  # ← SEM page.id
    
    setattr(page, 'status', PageStatus.PUBLISHED)  # ← Dinâmico
    db.commit()
    return {"message": "Página publicada"}

# Previsão (Draft para quem posta, não salva no público)

@admin_router.post("/pages/{slug}/preview")
async def preview_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=400, detail="Página não encontrada")

    current_status = getattr(page, 'status', '')
    if current_status != PageStatus.DRAFT:
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


