# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Importar routers
from app.api.v1.endpoints import analytics

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Crear app FastAPI
app = FastAPI(
    title="Trading Portfolio Analytics API",
    description="API profesional para análisis de operaciones de trading (similar a MyFxBook)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    analytics.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)

# Health check
@app.get("/")
async def root():
    """Endpoint raíz - Health check"""
    return {
        "status": "online",
        "service": "Trading Portfolio Analytics API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check detallado"""
    return {
        "status": "healthy",
        "service": "Trading Portfolio Analytics",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Iniciando Trading Portfolio Analytics API...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
