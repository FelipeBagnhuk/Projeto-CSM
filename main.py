from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from edit_page import admin_router
from public_route import public_router

app = FastAPI(title="PELP CMS API", version="1.0.0")

# Inclui routers PRIMEIRO
app.include_router(public_router)
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

from data_base import engine, Base  

# CRIAR TABELAS (rode UMA VEZ só)
Base.metadata.create_all(bind=engine)
print("✅ Tabelas criadas: pages, sections, collection_items!")