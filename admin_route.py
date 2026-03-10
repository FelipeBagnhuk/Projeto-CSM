from typing import List, Optional, cast, Any 
from models import Page, Section, SectionCreate, SectionRead, PageRead, Snapshot, SectionUpdate
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from edit_page import PageStatus
from models import Page, Section, SectionCreate, SectionRead, PageRead, Snapshot, PageUpdate, SectionsOrder
from data_base import SessionLocal
from sqlalchemy.types import JSON
import json
from typing import Optional
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy import String
from datetime import datetime



admin_router = APIRouter(prefix="/admin", tags=["Admin"])  

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Função da salvar snapshot

def save_snapshot(entity_id: str | int, action: str, snapshot_data: dict, db: Session):
    """Snapshot FLEXÍVEL para QUALQUER tipo de seção (texto, imagem, accordions)"""
    entity_id_str = str(entity_id)
    
    enhanced_data = {
        **snapshot_data,  # ← Preserva dados antigos
        "snapshot_version": "2.0",
        "timestamp": datetime.utcnow().isoformat(),
        "section_type_friendly": snapshot_data.get("section_type_friendly", "genérica")
    }
    
    snapshot = Snapshot(
        entity_id=entity_id_str,
        entity_type=snapshot_data.get("entity_type", "section"),
        action=action,
        data=enhanced_data
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
    return {
    "message": "Página publicada",
    "page_id": page.id,
    "entity_id": page.id  
}

#Reordenar seção

@admin_router.put("/pages/{slug}/sections/order")  
async def reorder_sections(slug: str, sections_order: List[int] = Body(embed=True), db: Session = Depends(get_db)):
    page = db.query(Page).filter(Page.slug == slug).first()
    if not page:
        raise HTTPException(status_code=404, detail="Página não encontrada")
    
    for i, section_id in enumerate(sections_order):
        section_query = db.query(Section).filter(
            Section.id == section_id, 
            Section.page_id == page.id
        )
        section = section_query.first()
        
        if section is not None: 
            setattr(section, 'order', i)  
    
    db.commit()
    return {"message": "Ordem atualizada"}


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
async def list_snapshots(entity_id: str, db: Session = Depends(get_db)):
    snapshots = db.query(Snapshot).filter(
        Snapshot.entity_id.cast(String) == entity_id
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
    snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot não encontrado")
    
    entity_id = int(snapshot.entity_id)
    data = snapshot.data
    
    # PAGE - com ANTES/DEPOIS
    if snapshot.entity_type == "page":
        page = db.query(Page).filter(Page.id == entity_id).first()
        if page:
            old_title = page.title
            old_status = page.status
            
            page.title = data.get("old_title", page.title)
            page.status = data.get("old_status", page.status)
            
            db.commit()
            return {
                "message": "Página restaurada!",
                "entity": "page",
                "was": {"title": old_title, "status": old_status},
                "now": {"title": page.title, "status": page.status}
            }
    
    # SECTION - com ANTES/DEPOIS  
    elif snapshot.entity_type == "section":
        section = db.query(Section).filter(Section.id == entity_id).first()
        if section:
            old_type = section.type
            old_content = section.content[:50] + "..." if section.content else ""
            old_order = section.order
            
            section.type = data.get("old_type", section.type) or ""
            section.content = data.get("old_content", section.content) or ""
            section.order = data.get("old_order", section.order) or 0
            
            db.commit()
            return {
                "message": "Seção restaurada!",
                "entity": "section", 
                "was": {"type": old_type, "content": old_content, "order": old_order},
                "now": {"type": section.type, "content": section.content[:50] + "...", "order": section.order}
            }
    
    raise HTTPException(status_code=400, detail="Tipo não suportado")