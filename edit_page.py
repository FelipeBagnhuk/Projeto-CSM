from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
from models import Page, Section, SectionCreate, SectionRead
from data_base import SessionLocal

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

admin_router = APIRouter(prefix="/admin", tags=["Admin"]) # vou dar um jeito de tirar isso daqui depois

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


