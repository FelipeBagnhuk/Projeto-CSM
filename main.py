from fastapi import FastAPI, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from edit_page import Page, SessionLocal
from public_route import public_router 

app = FastAPI(title="PELP CMS API", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inclui routers PRIMEIRO
app.include_router(public_router)
admin_router = APIRouter(prefix="/admin", tags=["Admin"])
app.include_router(admin_router)

# Monta arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Health check
@app.get("/")
def root():
    return {"message": "PELP CMS API rodando!", "status": "ok"}

# ROTA ADMIN - EDIÇÃO

app.include_router(admin_router)
    
    # Busca ou cria página
   

    
    # Deleta sections antigas
  
    
    # === HERO ===
 
    
    # === TEXT IMAGE ===
   

    
    # === TEXT CENTER ===
 
    # === ATIVOS ===
  
    
    # === DESAFIOS ===
  
    
  