# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    """Roles de usuario"""
    USER = "user"
    ADMIN = "admin"
    TRADER = "trader"

class OAuthProvider(str, Enum):
    """Proveedores OAuth"""
    GOOGLE = "google"
    GITHUB = "github"

# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Schema base de usuario"""
    email: EmailStr
    name: str
    image: Optional[str] = None
    role: UserRole = UserRole.USER

class UserCreate(BaseModel):
    """Schema para crear usuario (sign-up)"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña de al menos 8 caracteres")
    name: str
    image: Optional[str] = None

class UserLogin(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str

class UserInDB(UserBase):
    """Schema de usuario en DB (MongoDB)"""
    id: str = Field(alias="_id")
    password_hash: str
    email_verified: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "trader@example.com",
                "password_hash": "$2b$12$...",
                "name": "John Trader",
                "image": "https://example.com/avatar.jpg",
                "role": "trader",
                "email_verified": True,
                "created_at": "2025-12-03T12:00:00Z"
            }
        }

class UserResponse(UserBase):
    """Schema de respuesta de usuario (sin password_hash)"""
    id: str = Field(alias="_id")
    email_verified: bool
    created_at: datetime
    
    class Config:
        populate_by_name = True

# ============================================================================
# SESSION SCHEMAS
# ============================================================================

class SessionCreate(BaseModel):
    """Schema para crear sesión"""
    user_id: str
    
class SessionInDB(BaseModel):
    """Schema de sesión en DB"""
    id: str = Field(alias="_id")
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime
    
    class Config:
        populate_by_name = True

class SessionResponse(BaseModel):
    """Respuesta de sesión con datos de usuario"""
    user: UserResponse
    token: str
    expires_at: datetime

# ============================================================================
# VERIFICATION SCHEMAS
# ============================================================================

class VerificationCreate(BaseModel):
    """Schema para crear verificación"""
    identifier: str  # email o user_id
    code: str = Field(..., min_length=6, max_length=6)
    
class VerificationInDB(BaseModel):
    """Schema de verificación en DB"""
    id: str = Field(alias="_id")
    identifier: str
    code: str
    expires_at: datetime
    created_at: datetime
    
    class Config:
        populate_by_name = True

class VerifyEmailRequest(BaseModel):
    """Request para verificar email"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

# ============================================================================
# OAUTH ACCOUNT SCHEMAS
# ============================================================================

class OAuthAccountCreate(BaseModel):
    """Schema para crear cuenta OAuth"""
    user_id: str
    provider: OAuthProvider
    provider_id: str
    
class OAuthAccountInDB(BaseModel):
    """Schema de cuenta OAuth en DB"""
    id: str = Field(alias="_id")
    user_id: str
    provider: OAuthProvider
    provider_id: str  # ID del usuario en el provider (Google ID, GitHub ID)
    created_at: datetime
    
    class Config:
        populate_by_name = True

# ============================================================================
# PASSWORD RESET SCHEMAS
# ============================================================================

class ForgotPasswordRequest(BaseModel):
    """Request para solicitar reset de password"""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Request para resetear password"""
    token: str
    new_password: str = Field(..., min_length=8)

# ============================================================================
# TOKEN SCHEMAS
# ============================================================================

class TokenPayload(BaseModel):
    """Payload del JWT token"""
    sub: str  # user_id
    email: str
    role: UserRole
    exp: datetime

class TokenResponse(BaseModel):
    """Respuesta con token"""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
