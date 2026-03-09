from typing import List, Optional, cast, Any 
from models import Page, Section, SectionCreate, SectionRead, PageRead, Snapshot, SectionUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from edit_page import PageStatus
from models import Page, Section, SectionCreate, SectionRead, PageRead, Snapshot, PageUpdate
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

#Criar/editar página (subtitui tudo)

@admin_router.put("/pages/{slug}", response_model=PageRead)
async def update_page(slug: str, page_data: PageUpdate, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        page = Page(
            slug=slug, 
            title=page_data.title or "", 
            status=PageStatus.DRAFT  
        )
        db.add(page)
        db.commit()
        db.refresh(page)
        return page  
    
    if page_data.title is not None:
        page.title = page_data.title
    if page_data.status is not None:
        page.status = PageStatus(page_data.status)  
    
    db.commit()
    db.refresh(page)
    return page

#Lista as páginas:

@admin_router.get("/pages", response_model=List[PageRead]) 
async def list_pages(db: Session = Depends(get_db)):
    return db.query(Page).all()

#Criar seção: 

@admin_router.post("/pages/{slug}/sections", response_model=SectionRead)
async def create_section(
    slug: str,
    section_data: SectionCreate,
    db: Session = Depends(get_db)
):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")

    section = Section(
        page_id=page.id,
        type=section_data.type,     
        content=section_data.content, 
        order=section_data.order     
        # Removido title!
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return section

#Lista seções de uma página: 

@admin_router.get("/pages/{slug}/sections", response_model=List[SectionRead])
async def get_page_sections(slug: str, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    
    sections = db.query(Section).filter(Section.page_id == page.id).order_by(Section.order).all()
    return sections

# Publicar página: 

@admin_router.post("/pages/{slug}/publish")
async def publish_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")

    page_snapshot = {
    "entity_id": page.id,
    "entity_type": "page",
    "page_id": page.id,                    
    "page_slug": page.slug,                
    "old_status": page.status,
    "old_title": page.title,
    "action_info": "Página publicada"      
}

    save_snapshot(page.id, "page_published", page_snapshot, db)
    setattr(page, 'status', PageStatus.PUBLISHED)
    db.commit()
    return {f"message": "Página publicada", "page_id":{page.id}, "entily_id":{page.id}}

#Atualiza seção específica: 

@admin_router.put("/pages/{slug}/sections/{section_id}", response_model=SectionRead)
async def update_section(
    slug: str,
    section_data: SectionUpdate,  
    section_id: int,
    db: Session = Depends(get_db)
):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")

    section_query = db.query(Section).filter(
        Section.id == section_id,
        Section.page_id == page.id
    )
    section = section_query.first()
    if not section:
        raise HTTPException(status_code=404, detail="Seção não encontrada")

    # Snapshot 
    snapshot_data = {
        "entity_id": section_id,
        "entity_type": "section",
        "old_type": section.type or "",
        "old_content": section.content or "",
        "old_order": section.order or 0
    }
    save_snapshot(section_id, "section_update", snapshot_data, db)

    if section_data.content is not None:
        section.content = section_data.content
    if section_data.type is not None:
        section.type = section_data.type
    if section_data.order is not None:
        section.order = section_data.order

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
    @admin_router.get("/snapshots/{entity_id}", response_model=List)
    async def list_snapshots(entity_id: int, db: Session = Depends(get_db)):
        snapshots = db.query(Snapshot).filter(
            Snapshot.entity_id == str(entity_id)  # string por causa do save_snapshot
        ).order_by(Snapshot.created_at.desc()).all()
        
        return [
            {
                "id": snapshot.id,
                "entity_id": snapshot.entity_id,
                "entity_type": snapshot.entity_type,
                "action": snapshot.action,
                "data": snapshot.data,
                "created_at": snapshot.created_at.isoformat()
            }
            for snapshot in snapshots
        ]

# 9. Restaura Snapshot

@admin_router.post("/snapshots/{snapshot_id}/restore")
async def restore_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    # Implementar restauração
    pass


