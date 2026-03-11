from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from models import (
    Page, Section, PageRead, PageUpdate, SectionCreate, 
    SectionRead, SectionUpdate, Snapshot, SectionsOrder, PageUpdateBody, SectionsOrderBody
)
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from edit_page import PageStatus
from data_base import SessionLocal
from sqlalchemy.types import String
from datetime import datetime

admin_router = APIRouter(prefix="/admin", tags=["Admin"]) 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função da salvar snapshot

def save_snapshot(entity_id: str | int, action: str, snapshot_data: dict, db: Session):
    """Snapshot FLEXÍVEL para QUALQUER tipo de seção (texto, imagem, accordions)"""
    entity_id_str = str(entity_id)
    
    enhanced_data = {
        **snapshot_data,  
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

# Criar/editar página (substitui tudo)

# @admin_router.put("/pages/{slug}", response_model=PageRead, summary="Atualizar página completa")
# async def update_page(
#     slug: str,
#     page_data: PageUpdateBody,
#     db: Session = Depends(get_db)
# ):
#     page = db.query(Page).filter(Page.slug == slug).first()
#     if not page:
#         page = Page(
#             slug=slug, 
#             title=page_data.title or 'Nova Página', 
#             status=PageStatus.DRAFT  
#         )
#         db.add(page)
#         db.commit()
#         db.refresh(page)
#         return page  
    
#     # Só atualiza campos que vieram preenchidos
#     page_data_dict = page_data.dict(exclude_unset=True)
#     for key, value in page_data_dict.items():
#         if hasattr(page, key):
#             if key == 'status':
#                 setattr(page, key, getattr(PageStatus, str(value)))
#             else:
#                 setattr(page, key, value)
    
#     db.commit()
#     db.refresh(page)
#     return page

# Lista as páginas

@admin_router.get("/pages")
async def list_pages(db: Session = Depends(get_db)):
    return {"status": "db_ok", "message": "Admin funcionando!"}

#Criar seção  

# @admin_router.post("/pages/{slug}/sections", response_model=SectionRead)
# async def create_section(
#     slug: str,
#     section_data: SectionCreate,
#     db: Session = Depends(get_db)
# ):
#     page = db.query(Page).filter(Page.slug == slug).first()
#     if not page:
#         raise HTTPException(status_code=404, detail="Página não encontrada")

#     section = Section(
#         page_id=page.id,
#         type=section_data.type,     
#         content=section_data.content, 
#         order=section_data.order     
#     )
#     db.add(section)
#     db.commit()
#     db.refresh(section)
#     return section

# Lista seções de uma página  

# @admin_router.get("/pages/{slug}/sections", response_model=List[SectionRead])
# async def get_page_sections(slug: str, db: Session = Depends(get_db)):
#     page = db.query(Page).filter(Page.slug == slug).first()
#     if not page:
#         raise HTTPException(status_code=404, detail="Página não encontrada")
    
#     sections = db.query(Section).filter(Section.page_id == page.id).order_by(Section.order).all()
#     return sections

# Publicar página  

# @admin_router.post("/pages/{slug}/publish")
# async def publish_page(slug: str, db: Session = Depends(get_db)):
#     page = db.query(Page).filter(Page.slug == slug).first()
#     if not page:
#         raise HTTPException(status_code=404, detail="Página não encontrada")

#     page_snapshot = {
#         "entity_id": getattr(page, 'id', 0),      
#         "entity_type": "page",
#         "page_id": getattr(page, 'id', 0),        
#         "page_slug": page.slug,         
#         "old_status": getattr(page, 'status', ''),
#         "old_title": getattr(page, 'title', ''),
#         "action_info": "Página publicada"  
#     }

#     save_snapshot(getattr(page, 'id', 0), "page_published", page_snapshot, db)  
#     setattr(page, 'status', PageStatus.PUBLISHED)
#     db.commit()
#     return {
#         "message": "Página publicada",
#         "page_id": getattr(page, 'id', 0),        
#         "entity_id": getattr(page, 'id', 0)       
#     }

# Reordenar seção

# @admin_router.put("/pages/{slug}/sections/order")
# async def reorder_sections(
#     slug: str, 
#     body: SectionsOrderBody,
#     db: Session = Depends(get_db)
# ):
#     page = db.query(Page).filter(Page.slug == slug).first()
#     if not page:
#         raise HTTPException(status_code=404, detail="Página não encontrada")
    
#     sections_order = body.sections_order
#     for i, section_id in enumerate(sections_order):
#         section = db.query(Section).filter(
#             Section.id == section_id, 
#             Section.page_id == getattr(page, 'id', 0)
#         ).first()
        
#         if section: 
#             setattr(section, 'order', i)  
    
#     db.commit()
#     return {"message": "Ordem atualizada"}

# Atualiza seção específica  

# @admin_router.put("/pages/{slug}/sections/{section_id}", response_model=SectionRead)
# async def update_section(
#     slug: str, 
#     section_id: int,
#     section_data: SectionUpdate,
#     db: Session = Depends(get_db)
# ):
#     page = db.query(Page).filter(Page.slug == slug).first()
#     if not page:
#         raise HTTPException(status_code=404, detail="Página não encontrada")

#     section = db.query(Section).filter(
#         Section.id == section_id,
#         Section.page_id == getattr(page, 'id', 0)  
#     ).first()
#     if not section:
#         raise HTTPException(status_code=404, detail="Seção não encontrada")

#     snapshot_data = {
#         "entity_id": section_id,
#         "entity_type": "section",
#         "old_type": getattr(section, 'type', '') or "",
#         "old_content": getattr(section, 'content', '') or "",
#         "old_order": getattr(section, 'order', 0) or 0
#     }
#     save_snapshot(section_id, "section_update", snapshot_data, db)

#     # Atualiza só campos que vieram
#     if getattr(section_data, 'content', None) is not None:
#         setattr(section, 'content', getattr(section_data, 'content', ''))
#     if getattr(section_data, 'type', None) is not None:
#         setattr(section, 'type', getattr(section_data, 'type', ''))
#     if getattr(section_data, 'order', None) is not None:
#         setattr(section, 'order', int(getattr(section_data, 'order', 0)))

#     db.commit()
#     db.refresh(section)
#     return section

# Previsão (Draft para quem posta, não salva no público)

# @admin_router.post("/pages/{slug}/preview")
# async def preview_page(slug: str, db: Session = Depends(get_db)):
#     page = db.query(Page).filter(Page.slug == slug).first()
#     if not page:
#         raise HTTPException(status_code=400, detail="Página não encontrada")

#     current_status = getattr(page, 'status', '')
#     if current_status != PageStatus.DRAFT:
#         raise HTTPException(status_code=400, detail="Só drafts podem ter preview")
    
#     return {"preview_url": f"/preview/{slug}", "page": page}

# Lista Snapshots

# @admin_router.get("/snapshots/{entity_id}")
# async def list_snapshots(entity_id: str, db: Session = Depends(get_db)):
#     snapshots = db.query(Snapshot).filter(
#         Snapshot.entity_id.cast(String) == entity_id
#     ).order_by(Snapshot.created_at.desc()).all()
    
#     return [
#         {
#             "id": snapshot.id,
#             "entity_id": snapshot.entity_id,
#             "entity_type": snapshot.entity_type,
#             "action": snapshot.action,
#             "data": snapshot.data,
#             "created_at": snapshot.created_at.isoformat()
#         }
#         for snapshot in snapshots
#     ]

# Restaura Snapshot

# @admin_router.post("/snapshots/{snapshot_id}/restore")
# async def restore_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
#     snapshot = db.query(Snapshot).filter(Snapshot.id == snapshot_id).first()
#     if not snapshot:
#         raise HTTPException(status_code=404, detail="Snapshot não encontrado")
    
#     entity_id = int(getattr(snapshot, 'entity_id', 0))
#     snapshot_data = getattr(snapshot, 'data', {}) 
    
#     # PAGE
#     if getattr(snapshot, 'entity_type', '') == "page":
#         page = db.query(Page).filter(Page.id == entity_id).first()
#         if page:
#             old_title = getattr(page, 'title', '')
#             old_status = getattr(page, 'status', PageStatus.DRAFT)
            
#             setattr(page, 'title', snapshot_data.get("old_title", old_title))
#             setattr(page, 'status', PageStatus.DRAFT)
            
#             db.commit()
#             return {
#                 "message": "Página restaurada!",
#                 "entity": "page",
#                 "was": {"title": old_title, "status": str(old_status)},
#                 "now": {"title": getattr(page, 'title', ''), "status": str(getattr(page, 'status', ''))}
#             }
    
#     # SECTION
#     elif getattr(snapshot, 'entity_type', '') == "section":
#         section = db.query(Section).filter(Section.id == entity_id).first()
#         if section:
#             old_type = getattr(section, 'type', '')
#             old_content = (getattr(section, 'content', '')[:50] + "...") if getattr(section, 'content', '') else ""
#             old_order = getattr(section, 'order', 0)
            
#             setattr(section, 'type', snapshot_data.get("old_type", old_type))
#             setattr(section, 'content', snapshot_data.get("old_content", getattr(section, 'content', '')))
#             setattr(section, 'order', int(snapshot_data.get("old_order", old_order)))
            
#             db.commit()
#             return {
#                 "message": "Seção restaurada!",
#                 "entity": "section", 
#                 "was": {"type": old_type, "content": old_content, "order": old_order},
#                 "now": {"type": getattr(section, 'type', ''), "content": getattr(section, 'content', '')[:50] + "...", "order": getattr(section, 'order', 0)}
#             }
    
    raise HTTPException(status_code=400, detail="Tipo não suportado")
