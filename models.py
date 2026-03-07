from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from data_base import Base

# MODELOS PYDANTIC
class SectionCreate(BaseModel):  # Recebe do frontend
    type: str                      # "Menu-Icon_1"
    content: str                  
    order: Optional[int] = 0

class SectionRead(BaseModel):    # Envia pro frontend
    id: int                       # 1
    type: str
    content: str
    order: int
    
    class Config:
        from_attributes = True     # Lê do SQLAlchemy

# MODELOS BANCO
class Page(Base): #Página inteira
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True) #Incremental e não se repete 
    slug = Column(String(50), unique=True, index=True)
    title = Column(String(100))
    status = Column(String(20), default="pubished")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Section(Base): #As 48 sessões da página  
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
