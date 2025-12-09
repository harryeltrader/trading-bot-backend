# app/services/auth_service.py

from typing import Optional, Tuple
from datetime import datetime, timedelta
from bson import ObjectId
import logging

from app.schemas.auth import (
    UserCreate, UserInDB, UserResponse, UserLogin,
    SessionInDB, SessionResponse,
    VerificationInDB, VerifyEmailRequest,
    OAuthProvider, OAuthAccountInDB,
    ForgotPasswordRequest, ResetPasswordRequest,
    UserRole
)
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, verify_token,
    generate_verification_code, create_reset_token,
    decode_token
)
from app.utils.email import (
    send_verification_email,
    send_password_reset_email,
    send_welcome_email
)
from app.config.database import get_db

logger = logging.getLogger(__name__)

class AuthService:
    """Servicio de autenticación y gestión de usuarios"""
    
    def __init__(self):
        self.db = get_db()
    
    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================
    
    async def create_user(self, user_data: UserCreate) -> Tuple[UserResponse, str]:
        """
        Crear un nuevo usuario (sign-up).
        
        Args:
            user_data: Datos del usuario a crear
            
        Returns:
            Tupla (UserResponse, verification_code)
            
        Raises:
            ValueError: Si el usuario ya existe
        """
        # Verificar si el usuario ya existe
        existing_user = await self.db.users.find_one({"email": user_data.email})
        if existing_user:
            raise ValueError("El email ya está registrado")
        
        # Hash del password
        password_hash = hash_password(user_data.password)
        
        # Crear documento de usuario
        user_doc = {
            "email": user_data.email,
            "password_hash": password_hash,
            "name": user_data.name,
            "image": user_data.image,
            "role": UserRole.USER.value,
            "email_verified": False,
            "created_at": datetime.utcnow(),
            "updated_at": None
        }
        
        # Insertar en MongoDB
        result = await self.db.users.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        
        # Crear código de verificación
        verification_code = generate_verification_code()
        await self._create_verification(user_data.email, verification_code)
        
        # Enviar email de verificación
        try:
            send_verification_email(user_data.email, verification_code)
        except Exception as e:
            logger.error(f"Error enviando email de verificación: {str(e)}")
        
        # Convertir a UserResponse
        user_response = UserResponse(
            _id=user_doc["_id"],
            email=user_doc["email"],
            name=user_doc["name"],
            image=user_doc["image"],
            role=UserRole(user_doc["role"]),
            email_verified=user_doc["email_verified"],
            created_at=user_doc["created_at"]
        )
        
        logger.info(f"Usuario creado: {user_data.email}")
        return user_response, verification_code
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[UserInDB]:
        """
        Autenticar un usuario (sign-in).
        
        Args:
            login_data: Credenciales del usuario
            
        Returns:
            UserInDB si las credenciales son correctas, None si no
        """
        # Buscar usuario por email
        user_doc = await self.db.users.find_one({"email": login_data.email})
        if not user_doc:
            return None
        
        # Verificar password
        if not verify_password(login_data.password, user_doc["password_hash"]):
            return None
        
        # Convertir a UserInDB
        user_doc["_id"] = str(user_doc["_id"])
        user = UserInDB(**user_doc)
        
        logger.info(f"Usuario autenticado: {login_data.email}")
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """
        Obtener un usuario por ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            UserInDB si existe, None si no
        """
        try:
            user_doc = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user_doc:
                return None
            
            user_doc["_id"] = str(user_doc["_id"])
            return UserInDB(**user_doc)
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Obtener un usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            UserInDB si existe, None si no
        """
        user_doc = await self.db.users.find_one({"email": email})
        if not user_doc:
            return None
        
        user_doc["_id"] = str(user_doc["_id"])
        return UserInDB(**user_doc)
    
    async def update_user_verified(self, user_id: str) -> bool:
        """
        Marcar un usuario como verificado.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            True si se actualizó, False si no
        """
        try:
            result = await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"email_verified": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error actualizando usuario: {str(e)}")
            return False
    
    async def update_user_password(self, user_id: str, new_password: str) -> bool:
        """
        Actualizar la contraseña de un usuario.
        
        Args:
            user_id: ID del usuario
            new_password: Nueva contraseña
            
        Returns:
            True si se actualizó, False si no
        """
        try:
            password_hash = hash_password(new_password)
            result = await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password_hash": password_hash, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error actualizando password: {str(e)}")
            return False
    
    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================
    
    async def create_session(self, user: UserInDB) -> SessionResponse:
        """
        Crear una sesión para un usuario.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            SessionResponse con token y datos de usuario
        """
        # Crear JWT token
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role.value
        }
        access_token, expires_at = create_access_token(token_data)
        
        # Guardar sesión en MongoDB
        session_doc = {
            "user_id": user.id,
            "token": access_token,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.sessions.insert_one(session_doc)
        session_doc["_id"] = str(result.inserted_id)
        
        # Convertir usuario a UserResponse
        user_response = UserResponse(
            _id=user.id,
            email=user.email,
            name=user.name,
            image=user.image,
            role=user.role,
            email_verified=user.email_verified,
            created_at=user.created_at
        )
        
        logger.info(f"Sesión creada para usuario: {user.email}")
        
        return SessionResponse(
            user=user_response,
            token=access_token,
            expires_at=expires_at
        )
    
    async def get_session(self, token: str) -> Optional[SessionResponse]:
        """
        Obtener una sesión por token.
        
        Args:
            token: JWT token
            
        Returns:
            SessionResponse si la sesión es válida, None si no
        """
        # Verificar token
        token_payload = verify_token(token)
        if not token_payload:
            return None
        
        # Buscar sesión en MongoDB
        session_doc = await self.db.sessions.find_one({"token": token})
        if not session_doc:
            return None
        
        # Verificar si la sesión expiró
        if session_doc["expires_at"] < datetime.utcnow():
            await self.delete_session(token)
            return None
        
        # Obtener usuario
        user = await self.get_user_by_id(token_payload.sub)
        if not user:
            return None
        
        # Convert user to UserResponse
        user_response = UserResponse(
            _id=user.id,
            email=user.email,
            name=user.name,
            image=user.image,
            role=user.role,
            email_verified=user.email_verified,
            created_at=user.created_at
        )
        
        return SessionResponse(
            user=user_response,
            token=token,
            expires_at=session_doc["expires_at"]
        )
    
    async def delete_session(self, token: str) -> bool:
        """
        Eliminar una sesión (sign-out).
        
        Args:
            token: JWT token
            
        Returns:
            True si se eliminó, False si no
        """
        result = await self.db.sessions.delete_one({"token": token})
        if result.deleted_count > 0:
            logger.info("Sesión eliminada")
            return True
        return False
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Limpiar sesiones expiradas.
        
        Returns:
            Número de sesiones eliminadas
        """
        result = await self.db.sessions.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        if result.deleted_count > 0:
            logger.info(f"Sesiones expiradas eliminadas: {result.deleted_count}")
        return result.deleted_count
    
    # ========================================================================
    # VERIFICATION
    # ========================================================================
    
    async def _create_verification(self, identifier: str, code: str) -> VerificationInDB:
        """
        Crear una verificación (interno).
        
        Args:
            identifier: Email o user_id
            code: Código de verificación
            
        Returns:
            VerificationInDB
        """
        # Eliminar verificaciones anteriores
        await self.db.verifications.delete_many({"identifier": identifier})
        
        # Crear nueva verificación (expira en 15 minutos)
        verification_doc = {
            "identifier": identifier,
            "code": code,
            "expires_at": datetime.utcnow() + timedelta(minutes=15),
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.verifications.insert_one(verification_doc)
        verification_doc["_id"] = str(result.inserted_id)
        
        return VerificationInDB(**verification_doc)
    
    async def verify_email(self, verify_data: VerifyEmailRequest) -> bool:
        """
        Verificar el email de un usuario.
        
        Args:
            verify_data: Email y código de verificación
            
        Returns:
            True si se verificó correctamente, False si no
        """
        # Buscar verificación
        verification = await self.db.verifications.find_one({
            "identifier": verify_data.email,
            "code": verify_data.code
        })
        
        if not verification:
            logger.warning(f"Código de verificación inválido para: {verify_data.email}")
            return False
        
        # Verificar si expiró
        if verification["expires_at"] < datetime.utcnow():
            logger.warning(f"Código de verificación expirado para: {verify_data.email}")
            return False
        
        # Obtener usuario
        user = await self.get_user_by_email(verify_data.email)
        if not user:
            return False
        
        # Actualizar usuario como verificado
        await self.update_user_verified(user.id)
        
        # Eliminar verificación
        await self.db.verifications.delete_one({"_id": verification["_id"]})
        
        # Enviar email de bienvenida
        try:
            send_welcome_email(user.email, user.name)
        except Exception as e:
            logger.error(f"Error enviando email de bienvenida: {str(e)}")
        
        logger.info(f"Email verificado: {verify_data.email}")
        return True
    
    async def resend_verification_code(self, email: str) -> Optional[str]:
        """
        Reenviar código de verificación.
        
        Args:
            email: Email del usuario
            
        Returns:
            Código de verificación si se envió, None si no
        """
        # Verificar que el usuario existe
        user = await self.get_user_by_email(email)
        if not user:
            return None
        
        # Verificar que no está ya verificado
        if user.email_verified:
            return None
        
        # Crear nuevo código
        verification_code = generate_verification_code()
        await self._create_verification(email, verification_code)
        
        # Enviar email
        try:
            send_verification_email(email, verification_code)
            logger.info(f"Código de verificación reenviado a: {email}")
            return verification_code
        except Exception as e:
            logger.error(f"Error reenviando código: {str(e)}")
            return None
    
    # ========================================================================
    # PASSWORD RESET
    # ========================================================================
    
    async def forgot_password(self, request: ForgotPasswordRequest) -> bool:
        """
        Solicitar reset de password.
        
        Args:
            request: Email del usuario
            
        Returns:
            True si se envió el email, False si no
        """
        # Verificar que el usuario existe
        user = await self.get_user_by_email(request.email)
        if not user:
            # Por seguridad, no revelar si el email existe o no
            logger.warning(f"Intento de reset de password para email no existente: {request.email}")
            return True
        
        # Crear token de reset
        reset_token, expires_at = create_reset_token(user.email)
        
        # Guardar en verificaciones (reutilizamos la colección)
        await self._create_verification(user.email, reset_token)
        
        # Enviar email
        try:
            send_password_reset_email(user.email, reset_token)
            logger.info(f"Email de reset de password enviado a: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email de reset: {str(e)}")
            return False
    
    async def reset_password(self, request: ResetPasswordRequest) -> bool:
        """
        Resetear password con token.
        
        Args:
            request: Token y nueva contraseña
            
        Returns:
            True si se reseteó, False si no
        """
        # Decodificar token
        payload = decode_token(request.token)
        if not payload or payload.get("type") != "password_reset":
            logger.warning("Token de reset inválido")
            return False
        
        email = payload.get("email")
        if not email:
            return False
        
        # Obtener usuario
        user = await self.get_user_by_email(email)
        if not user:
            return False
        
        # Actualizar password
        success = await self.update_user_password(user.id, request.new_password)
        
        if success:
            # Eliminar todas las sesiones del usuario
            await self.db.sessions.delete_many({"user_id": user.id})
            logger.info(f"Password reseteado para: {email}")
        
        return success
    
    # ========================================================================
    # OAUTH
    # ========================================================================
    
    async def create_oauth_account(
        self,
        user_id: str,
        provider: OAuthProvider,
        provider_id: str
    ) -> OAuthAccountInDB:
        """
        Crear una cuenta OAuth.
        
        Args:
            user_id: ID del usuario
            provider: Proveedor OAuth (Google, GitHub)
            provider_id: ID del usuario en el proveedor
            
        Returns:
            OAuthAccountInDB
        """
        account_doc = {
            "user_id": user_id,
            "provider": provider.value,
            "provider_id": provider_id,
            "created_at": datetime.utcnow()
        }
        
        result = await self.db.accounts.insert_one(account_doc)
        account_doc["_id"] = str(result.inserted_id)
        
        logger.info(f"Cuenta OAuth creada: {provider.value} para usuario {user_id}")
        return OAuthAccountInDB(**account_doc)
    
    async def get_oauth_account(
        self,
        provider: OAuthProvider,
        provider_id: str
    ) -> Optional[OAuthAccountInDB]:
        """
        Obtener una cuenta OAuth.
        
        Args:
            provider: Proveedor OAuth
            provider_id: ID del usuario en el proveedor
            
        Returns:
            OAuthAccountInDB si existe, None si no
        """
        account_doc = await self.db.accounts.find_one({
            "provider": provider.value,
            "provider_id": provider_id
        })
        
        if not account_doc:
            return None
        
        account_doc["_id"] = str(account_doc["_id"])
        return OAuthAccountInDB(**account_doc)
