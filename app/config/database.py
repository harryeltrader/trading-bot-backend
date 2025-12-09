# app/config/database.py

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Configuración de MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "trading_bot_db")

class MongoDB:
    """Singleton para conexión a MongoDB"""
    
    client: Optional[AsyncIOMotorClient] = None
    database = None
    
    @classmethod
    async def connect_db(cls):
        """Conectar a MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(MONGODB_URL)
            cls.database = cls.client[DATABASE_NAME]
            
            # Verificar conexión
            await cls.client.admin.command('ping')
            logger.info(f"✅ Conectado a MongoDB: {DATABASE_NAME}")
            
            # Crear índices
            await cls.create_indexes()
            
        except Exception as e:
            logger.error(f"❌ Error conectando a MongoDB: {str(e)}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Cerrar conexión a MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB desconectado")
    
    @classmethod
    async def create_indexes(cls):
        """Crear índices en las colecciones"""
        try:
            # Índices para users
            await cls.database.users.create_index("email", unique=True)
            await cls.database.users.create_index("created_at")
            
            # Índices para sessions
            await cls.database.sessions.create_index("user_id")
            await cls.database.sessions.create_index("token", unique=True)
            await cls.database.sessions.create_index("expires_at")
            
            # Índices para verifications
            await cls.database.verifications.create_index("identifier")
            await cls.database.verifications.create_index("expires_at")
            
            # Índices para accounts (OAuth)
            await cls.database.accounts.create_index([("provider", 1), ("provider_id", 1)], unique=True)
            await cls.database.accounts.create_index("user_id")
            
            logger.info("✅ Índices de MongoDB creados")
            
        except Exception as e:
            logger.warning(f"⚠️ Error creando índices: {str(e)}")
    
    @classmethod
    def get_database(cls):
        """Obtener instancia de la base de datos"""
        if cls.database is None:
            raise Exception("Database no está conectada. Llama a connect_db() primero.")
        return cls.database

# Función helper para obtener la base de datos
def get_db():
    """Dependency para FastAPI"""
    return MongoDB.get_database()
