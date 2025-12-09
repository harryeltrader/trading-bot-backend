# app/utils/security.py

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
import os
from app.schemas.auth import TokenPayload, UserRole

# Configuración
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ============================================================================
# PASSWORD FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash una contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar si una contraseña coincide con su hash.
    
    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Hash de la contraseña
        
    Returns:
        True si coinciden, False si no
    """
    return pwd_context.verify(plain_password, hashed_password)

# ============================================================================
# JWT TOKEN FUNCTIONS
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, datetime]:
    """
    Crear un JWT access token.
    
    Args:
        data: Datos a incluir en el token (user_id, email, role)
        expires_delta: Tiempo de expiración opcional
        
    Returns:
        Tupla (token, expires_at)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt, expire

def verify_token(token: str) -> Optional[TokenPayload]:
    """
    Verificar y decodificar un JWT token.
    
    Args:
        token: JWT token a verificar
        
    Returns:
        TokenPayload si el token es válido, None si no
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        exp: int = payload.get("exp")
        
        if user_id is None or email is None:
            return None
        
        return TokenPayload(
            sub=user_id,
            email=email,
            role=UserRole(role) if role else UserRole.USER,
            exp=datetime.fromtimestamp(exp)
        )
    except jwt.PyJWTError:
        return None

def decode_token(token: str) -> Optional[dict]:
    """
    Decodificar un token sin verificar (útil para tokens de reset).
    
    Args:
        token: Token a decodificar
        
    Returns:
        Payload del token o None si es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# ============================================================================
# VERIFICATION CODE GENERATOR
# ============================================================================

def generate_verification_code() -> str:
    """
    Generar un código de verificación de 6 dígitos.
    
    Returns:
        Código de 6 dígitos
    """
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def create_reset_token(email: str) -> tuple[str, datetime]:
    """
    Crear un token para reset de password.
    
    Args:
        email: Email del usuario
        
    Returns:
        Tupla (token, expires_at)
    """
    expire = datetime.utcnow() + timedelta(hours=1)  # Expira en 1 hora
    to_encode = {
        "email": email,
        "type": "password_reset",
        "exp": expire
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token, expire
