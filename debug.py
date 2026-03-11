# debug.py - VERSÃO FINAL PARA DIAGNOSTICAR
from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import JSONResponse
import traceback
import logging

# Configura logging VERBOSE
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Debug FastAPI - Swagger Killer",
    docs_url="/docs",
    redoc_url=None,
    swagger_ui_parameters={"tryItOutEnabled": False}
)

debug_router = APIRouter(prefix="/debug", tags=["Debug"])

# Teste 1: Router básico
@debug_router.get("/test1")
async def test1():
    return {"message": "Router OK ✅"}

# Teste 2: Sem DB  
@debug_router.get("/test2")
async def test2():
    return {"status": "sem_db", "ok": True}

# Teste 3: COM DB (com try/catch)
@debug_router.get("/test3")
async def test3():
    try:
        from data_base import SessionLocal
        from sqlalchemy.orm import Session
        
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        # Chama Depends internamente
        db_gen = get_db()
        db = next(db_gen)
        next(db_gen)  # fecha generator
        
        return {"status": "db_ok", "ok": True}
    except Exception as e:
        logger.error(f"DB ERROR: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e), "trace": traceback.format_exc()}

# Teste 4: Admin_router SIMULADO
@debug_router.get("/admin/pages")
async def admin_pages():
    try:
        from admin_route import admin_router  # ← Testa import
        return {"admin_import": "OK"}
    except Exception as e:
        return {"admin_import_error": str(e)}

# Global error handler
@app.exception_handler(500)
async def global_exception_handler(request, exc):
    logger.error(f"500 ERROR: {exc}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "trace": traceback.format_exc()}
    )

app.include_router(debug_router)

# Startup debug
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 FastAPI startup OK!")
    logger.info(f"OpenAPI URL: /openapi.json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
