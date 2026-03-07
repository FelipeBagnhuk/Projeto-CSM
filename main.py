from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import edit_page
from edit_page import Page
from fastapi import APIRouter, Depends, HTTPException
from edit_page import SessionLocal
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from edit_page import DATABASE_URL

app = FastAPI()
engine = create_async_engine(DATABASE_URL)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/edit", tags=["PELP Digital Page Editor"])

app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)
app.include_router(edit_page.router)

# ROTA PÚBLICA - VISUALIZAÇÃO

@app.get("/public")
async def public_view(db: Session = Depends(get_db)):
    pages = db.scalars(db.select(Page)).all()
    return pages
