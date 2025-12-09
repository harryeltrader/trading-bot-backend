# app/api/v1/endpoints/auth.py

from fastapi import APIRouter, HTTPException, Depends, status, Header
from typing import Optional
import logging

from app.schemas.auth import (
    UserCreate, UserResponse, UserLogin,
    SessionResponse,
    VerifyEmailRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.services.auth_service import AuthService
from app.utils.security import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()

# ============================================================================
# DEPENDENCY: Get current user from token
# ============================================================================

async def get_current_user(authorization: Optional[str] = Header(None)) -> UserResponse:
    """
    Dependency para obtener el usuario actual desde el token.
    
    Args:
        authorization: Header de Authorization (Bearer token)
        
    Returns:
        UserResponse del usuario autenticado
        
    Raises:
        HTTPException 401 si el token es inválido
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado"
        )
    
    token = authorization.replace("Bearer ", "")
    auth_service = AuthService()
    session = await auth_service.get_session(token)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    return session.user

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/sign-up", response_model=dict, status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserCreate):
    """
    Registrar un nuevo usuario.
    
    - **email**: Email único del usuario
    - **password**: Contraseña (mínimo 8 caracteres)
    - **name**: Nombre completo
    - **image**: URL de imagen de perfil (opcional)
    
    Returns:
        - Usuario creado y código de verificación (solo en dev)
    """
    auth_service = AuthService()
    
    try:
        user, verification_code = await auth_service.create_user(user_data)
        
        logger.info(f"Usuario registrado: {user.email}")
        
        return {
            "success": True,
            "message": "Usuario creado exitosamente. Revisa tu email para verificar tu cuenta.",
            "user": user.model_dump(by_alias=True),
            "verification_code": verification_code  # TODO: Remover en producción
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error en sign-up: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/sign-in", response_model=SessionResponse)
async def sign_in(login_data: UserLogin):
    """
    Autenticar un usuario (login).
    
    - **email**: Email del usuario
    - **password**: Contraseña
    
    Returns:
        - Sesión con token de acceso y datos del usuario
    """
    auth_service = AuthService()
    
    # Autenticar usuario
    user = await auth_service.authenticate_user(login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )
    
    # Verificar si el email está verificado
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email no verificado. Por favor verifica tu email antes de iniciar sesión."
        )
    
    # Crear sesión
    session = await auth_service.create_session(user)
    
    logger.info(f"Usuario autenticado: {user.email}")
    
    return session

@router.post("/sign-out", response_model=dict)
async def sign_out(authorization: Optional[str] = Header(None)):
    """
    Cerrar sesión (invalidar token).
    
    Requiere:
        - Authorization header con Bearer token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado"
        )
    
    token = authorization.replace("Bearer ", "")
    auth_service = AuthService()
    
    success = await auth_service.delete_session(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sesión no encontrada"
        )
    
    logger.info("Usuario cerró sesión")
    
    return {
        "success": True,
        "message": "Sesión cerrada exitosamente"
    }

@router.get("/session", response_model=SessionResponse)
async def get_session(current_user: UserResponse = Depends(get_current_user)):
    """
    Obtener información de la sesión actual.
    
    Requiere:
        - Authorization header con Bearer token
        
    Returns:
        - Datos del usuario y sesión activa
    """
    # El current_user ya viene validado por el Dependency
    auth_service = AuthService()
    
    # Obtener sesión completa (para incluir expires_at)
    # En producción, podrías cachear esto o incluirlo en el JWT
    return {
        "user": current_user,
        "token": "current_token",  # Placeholder
        "expires_at": "2025-12-10T00:00:00Z"  # Placeholder
    }

# ============================================================================
# EMAIL VERIFICATION ENDPOINTS
# ============================================================================

@router.post("/verify-email", response_model=dict)
async def verify_email(verify_data: VerifyEmailRequest):
    """
    Verificar el email de un usuario con código de 6 dígitos.
    
    - **email**: Email del usuario
    - **code**: Código de verificación de 6 dígitos
    
    Returns:
        - Confirmación de verificación
    """
    auth_service = AuthService()
    
    success = await auth_service.verify_email(verify_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de verificación inválido o expirado"
        )
    
    logger.info(f"Email verificado: {verify_data.email}")
    
    return {
        "success": True,
        "message": "Email verificado exitosamente. Ya puedes iniciar sesión."
    }

@router.post("/resend-verification", response_model=dict)
async def resend_verification(email: str):
    """
    Reenviar código de verificación.
    
    - **email**: Email del usuario
    
    Returns:
        - Confirmación de envío
    """
    auth_service = AuthService()
    
    verification_code = await auth_service.resend_verification_code(email)
    
    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo reenviar el código. Verifica que el email sea correcto y no esté ya verificado."
        )
    
    logger.info(f"Código de verificación reenviado a: {email}")
    
    return {
        "success": True,
        "message": "Código de verificación reenviado. Revisa tu email.",
        "verification_code": verification_code  # TODO: Remover en producción
    }

# ============================================================================
# PASSWORD RESET ENDPOINTS
# ============================================================================

@router.post("/forgot-password", response_model=dict)
async def forgot_password(request: ForgotPasswordRequest):
    """
    Solicitar reset de contraseña.
    
    - **email**: Email del usuario
    
    Returns:
        - Confirmación de envío de email
    """
    auth_service = AuthService()
    
    await auth_service.forgot_password(request)
    
    # Por seguridad, siempre devolver éxito
    logger.info(f"Solicitud de reset de password para: {request.email}")
    
    return {
        "success": True,
        "message": "Si el email existe, recibirás instrucciones para restablecer tu contraseña."
    }

@router.post("/reset-password", response_model=dict)
async def reset_password(request: ResetPasswordRequest):
    """
    Restablecer contraseña con token.
    
    - **token**: Token de reset recibido por email
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)
    
    Returns:
        - Confirmación de cambio de contraseña
    """
    auth_service = AuthService()
    
    success = await auth_service.reset_password(request)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado"
        )
    
    logger.info("Contraseña restablecida exitosamente")
    
    return {
        "success": True,
        "message": "Contraseña restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña."
    }

# ============================================================================
# OAUTH ENDPOINTS (Placeholder para implementación futura)
# ============================================================================

@router.get("/oauth/{provider}")
async def oauth_login(provider: str):
    """
    Iniciar flujo OAuth con un proveedor (Google, GitHub).
    
    - **provider**: Proveedor OAuth (google, github)
    
    Returns:
        - URL de autorización del proveedor
    """
    # TODO: Implementar OAuth flow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"OAuth con {provider} no implementado aún"
    )

@router.get("/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: str):
    """
    Callback de OAuth (manejado por el proveedor).
    
    - **provider**: Proveedor OAuth
    - **code**: Código de autorización
    
    Returns:
        - Sesión con token de acceso
    """
    # TODO: Implementar OAuth callback
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"OAuth callback para {provider} no implementado aún"
    )

# ============================================================================
# ADMIN ENDPOINTS (Requieren role de admin)
# ============================================================================

@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    Obtener información del usuario actual.
    
    Requiere:
        - Authorization header con Bearer token
    """
    return current_user

@router.delete("/sessions/cleanup", response_model=dict)
async def cleanup_expired_sessions(current_user: UserResponse = Depends(get_current_user)):
    """
    Limpiar sesiones expiradas (solo admin).
    
    Requiere:
        - Authorization header con Bearer token
        - Role de admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol de administrador."
        )
    
    auth_service = AuthService()
    deleted_count = await auth_service.cleanup_expired_sessions()
    
    logger.info(f"Sesiones expiradas limpiadas: {deleted_count}")
    
    return {
        "success": True,
        "message": f"Se eliminaron {deleted_count} sesiones expiradas"
    }
