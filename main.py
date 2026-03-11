# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
# from edit_page import admin_router as edit_router  
# from public_route import public_router
# from admin_route import admin_router as admin_router  

# from data_base import engine 
# from models import Base 

# app = FastAPI(title="PELP CMS API", version="1.0.0")


# app.include_router(public_router)
# app.include_router(edit_router)     
# #app.include_router(admin_router)    


# app.mount("/static", StaticFiles(directory="static"), name="static")
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# @app.get("/")
# def root():
#     return {"message": "PELP CMS API rodando!", "status": "ok"}

from fastapi import FastAPI

app = FastAPI(title="TESTE MÍNIMO")

@app.get("/")
def root():
    return {"message": "PELP CMS API rodando!", "status": "ok"}

@app.get("/test")
def test():
    return {"test": "ok"}