from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, create_engine
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, sessionmaker 
from enum import Enum


# Base LOCAL 
class Base(DeclarativeBase):
    pass

# MODELOS PYDANTIC 
class SectionCreate(BaseModel):  
    type: str                  
    content: str  
    order: Optional[int] = 0

class SectionRead(BaseModel):    
    id: int           
    type: str
    content: str
    order: int
    
    class Config:
        from_attributes = True     

class PageRead(BaseModel): 
    id: int
    slug: str
    title: str
    status: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class PageCreate(BaseModel):  
    slug: str
    title: str
    status: str = "draft"

class SectionUpdate(BaseModel):
    content: Optional[str] = None
    type: Optional[str] = None
    order: Optional[int] = None    

# MODELOS BANCO

class Page(Base): 
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True)
    slug = Column(String(50), unique=True, index=True)
    title = Column(String(100))
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Section(Base): 
    __tablename__ = "sections" 
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    type = Column(String(50), nullable=False)     
    content = Column(Text)                 
    order = Column(Integer, default=0)    

class CollectionItem(Base):  
    __tablename__ = "collection_items"
    
    id = Column(Integer, primary_key=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, default=0)

class Snapshot(Base):
    __tablename__ = "snapshots"
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, nullable=False)
    entity_type = Column(String(20), nullable=False)
    action = Column(String(50), nullable=False)
    data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())    


class PageUpdate(BaseModel):
    title: str | None = None
    status: str | None = None 

class SectionsOrder(BaseModel):
    sections_order: List[int]
