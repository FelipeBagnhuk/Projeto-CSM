from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.sql import func
from typing import List
import json



DATABASE_URL = "postgresql://postgres:pstgr3word@localhost:5432/pelp_cms" 
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ENUMS:

class PageStatus:
    DRAFT= "draft" #rascunho, pagína sendo editada e não publicada
    PUBLISHED = "published" #publicado, no ar e visível
    ARQUIVED = "archived" #arquivado, ou página antiga 

class SectionType:
    MENU_ICON_1 = "Menu-Icon_1"   # Home
    MENU_ICON_2 = "Menu-Icon_2"   # Sobre  
    MENU_ICON_3 = "Menu-Icon_3"   # PELP
    MENU_ICON_4 = "Menu-Icon_4"   # Dimensões
    MENU_ICON_5 = "Menu-Icon_5"   # Notícias
    MENU_ICON_6 = "Menu-Icon_6"   # Documentos
    MENU_ICON_7 = "Menu-Icon_7"   # User Icon 7
    MENU_ICON_8 = "Menu-Icon_8"   # User Icon 8
    MENU_ICON_9 = "Menu-Icon_9"   # User Icon 9
    MENU_ICON_10 = "Menu-Icon_10" # User Icon10
    MAINTITLE= "MainTitle" #Título principal. (Sustentável. Inclusiva. Inovadora)
    MAIN_SUBTITLE = "Subtitle" #Subtítulo do título principal. (A Paraíba do futuro. Feita por paraibanos para todos)
    BACKGROUND_IMAGE="Background-Image" #Imagem de fundo na sessão hero
    TITLE_IMAGE = "Title-Image" #Sessão de texto com imagem lateral ("O que é o plano estratégico de longo prazo da Paraíba")
    IMAGE_RIGHT="Image-right" #Imagem à direita do texto
    TEXT_IMAGE="Text-Image" #Texto à esquerda da imagem ("O plano estratégico...")
    TITLE_CENTER="Title-Center" #Título centralizado ("Onde estamos")
    TEXT_CENTER="Text-Center" #Texto centralizado ("A Paraíba Construiu...")
    TITLE_ACCORDIONS_A="Title-Accordions_A" #Título do primeiro accordion ("Ativos")
    TITLE_ACCORDION_A1="Title-Accordion_A1" #Título do primeiro acordion na sessão "ativos"
    BALOON_ACCORDION_A1_1 = "Baloon-Accordion_A1_1"  # Primeiro do A1
    BALOON_ACCORDION_A1_2 = "Baloon-Accordion_A1_2"  # Segundo balão do A1  
    BALOON_ACCORDION_A1_3 = "Baloon-Accordion_A1_3"  # Terceiro balão do A1 
    TITLE_ACCORDION_A2="Title-Accordion_A2" #Título do segundo accordion na sessão "ativos"
    BALOON_ACCORDION_A2_1 = "Baloon-Accordion_A2_1"  # Primeiro do A2
    BALOON_ACCORDION_A2_2 = "Baloon-Accordion_A2_2"  # Segundo balão do A2  
    BALOON_ACCORDION_A2_3 = "Baloon-Accordion_A2_3"  # Terceiro balão do A2
    TITLE_ACCORDION_A3="Title-Accordion_A3" #Título do terceiro accordion na sessão "ativos"
    BALOON_ACCORDION_A3_1 = "Baloon-Accordion_A3_1"  # Primeiro do A3
    BALOON_ACCORDION_A3_2 = "Baloon-Accordion_A3_2"  # Segundo balão do A3  
    BALOON_ACCORDION_A3_3 = "Baloon-Accordion_A3_3"  # Terceiro balão do A3
    TITLE_ACCORDION_A4="Title-Accordion_A4" #Título do quarto accordion na sessão "ativos"
    BALOON_ACCORDION_A4_1 = "Baloon-Accordion_A4_1"  # Primeiro do A4
    BALOON_ACCORDION_A4_2 = "Baloon-Accordion_A4_2"  # Segundo balão do A4
    BALOON_ACCORDION_A4_3 = "Baloon-Accordion_A4_3"  # Terceiro balão do A4
    TITLE_ACCORDIONS_B="Title-Accordions_B" #Título do segundo acccordion ("Desafios")
    TITLE_ACCORDION_B1="Title-Accordion_B1" #Título do primeiro accordion na sessão "desafios" 
    BALOON_ACCORDION_B1_1 = "Baloon-Accordion_B1_1"  # Primeiro do B1
    BALOON_ACCORDION_B1_2 = "Baloon-Accordion_B1_2"  # Segundo balão do B1
    BALOON_ACCORDION_B1_3 = "Baloon-Accordion_B1_3"  # Terceiro balão do B1
    TITLE_ACCORDION_B2="Title-Accordion_B2" #Título do segundo accordion na sessão "desafios" 
    BALOON_ACCORDION_B2_1 = "Baloon-Accordion_B2_1"  # Primeiro do B2
    BALOON_ACCORDION_B2_2 = "Baloon-Accordion_B2_2"  # Segundo balão do B2
    BALOON_ACCORDION_B2_3 = "Baloon-Accordion_B2_3"  # Terceiro balão do B2
    TITLE_ACCORDION_B3="Title-Accordion_B3" #Título do terceiro accordion na sessão "desafios"
    BALOON_ACCORDION_B3_1 = "Baloon-Accordion_B3_1"  # Primeiro do B3
    BALOON_ACCORDION_B3_2 = "Baloon-Accordion_B3_2"  # Segundo balão do B3
    BALOON_ACCORDION_B3_3 = "Baloon-Accordion_B3_3"  # Terceiro balão do B3
    TITLE_ACCORDION_B4="Title-Accordion_B4" #Título do quarto accordion na sessão "desafios" 
    BALOON_ACCORDION_B4_1 = "Baloon-Accordion_B4_1"  # Primeiro do B4
    BALOON_ACCORDION_B4_2 = "Baloon-Accordion_B4_2"  # Segundo balão do B4
    BALOON_ACCORDION_B4_3 = "Baloon-Accordion_B4_3"  # Terceiro balão do B4

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



    
    
    # Snapshot
  


# UTILITÁRIOS


