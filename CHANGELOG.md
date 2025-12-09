# Changelog

## [2.0.0] - 2025-12-03 - Sistema de Autenticación Completo 🔐

### ✨ Nuevas características principales

#### Sistema de Autenticación (Auth Service Microservice)
- **Registro de usuarios (Sign-up)**
  - Validación de email único
  - Hash seguro de contraseñas con bcrypt
  - Generación automática de código de verificación
  - Envío de email de verificación con template HTML profesional

- **Autenticación (Sign-in/Sign-out)**
  - Login con email y password
  - Generación de JWT tokens (HS256)
  - Sesiones persistentes en MongoDB
  - Invalidación de sesiones (logout)
  - Validación de email verificado antes de login

- **Verificación de Email**
  - Código de 6 dígitos con expiración de 15 minutos
  - Endpoint para reenviar código
  - Email de bienvenida después de verificar
  - Templates HTML profesionales con gradientes

- **Recuperación de Contraseña**
  - Solicitud de reset con envío de email
  - Token JWT con expiración de 1 hora
  - Flow completo de password reset
  - Invalidación de todas las sesiones al resetear

- **Gestión de Sesiones**
  - Almacenamiento en MongoDB con índices optimizados
  - Validación automática en cada request
  - Limpieza de sesiones expiradas (endpoint admin)
  - Token incluye user_id, email, y role

- **Roles de Usuario**
  - `user`: Usuario normal
  - `trader`: Trader con permisos especiales
  - `admin`: Administrador del sistema

- **OAuth (Estructura preparada)**
  - Endpoints definidos para Google y GitHub
  - Schema para cuentas OAuth
  - Base de datos lista (colección `accounts`)

### 🗄️ Base de Datos MongoDB

#### Nuevas colecciones
- **users**: Información de usuarios
  - Campos: email, password_hash, name, image, role, email_verified, created_at
  - Índices: email (unique), created_at

- **sessions**: Sesiones activas
  - Campos: user_id, token, expires_at, created_at
  - Índices: user_id, token (unique), expires_at

- **verifications**: Códigos de verificación
  - Campos: identifier, code, expires_at, created_at
  - Índices: identifier, expires_at

- **accounts**: Cuentas OAuth
  - Campos: user_id, provider, provider_id, created_at
  - Índices: user_id, [provider, provider_id] (compound unique)

### 🔧 Cambios técnicos

#### Nuevos archivos
- `app/schemas/auth.py`: Schemas Pydantic para autenticación
- `app/services/auth_service.py`: Lógica de negocio de autenticación
- `app/api/v1/endpoints/auth.py`: Endpoints de autenticación
- `app/config/database.py`: Conexión MongoDB con Motor
- `app/utils/security.py`: Utilidades de seguridad (hash, JWT)
- `app/utils/email.py`: Envío de emails con templates HTML

#### Archivos modificados
- `app/main.py`: 
  - Agregado router de autenticación
  - Eventos de startup/shutdown para MongoDB
  - Actualizada versión a 2.0.0

- `.env.example`: 
  - Variables de MongoDB
  - Configuración JWT
  - Configuración SMTP
  - OAuth credentials

- `requirements.txt`:
  - motor==3.3.2 (MongoDB async)
  - passlib[bcrypt]==1.7.4 (Password hashing)
  - PyJWT==2.8.0 (JWT tokens)
  - python-jose[cryptography]==3.3.0 (Crypto)

### 🔒 Seguridad

- Password hashing con bcrypt (cost factor configurable)
- JWT tokens con HS256 algorithm
- Tokens de expiración configurable (default: 7 días)
- Reset tokens de 1 hora de expiración
- Verification codes de 15 minutos de expiración
- Salt automático en passwords
- Validación de email antes de login

### 📧 Sistema de Emails

- Templates HTML profesionales con gradientes
- Soporte SMTP (Gmail, SendGrid, Mailgun, etc)
- 3 tipos de emails:
  1. Verificación de email (código de 6 dígitos)
  2. Reset de password (link con token)
  3. Bienvenida (después de verificar)

### 📚 Documentación

- `README.md`: Actualizado con información completa
- `AUTH-SERVICE-IMPLEMENTACION.md`: Documentación detallada del Auth Service
- Swagger UI actualizada en `/docs`
- ReDoc actualizada en `/redoc`

### 🎯 Endpoints principales

#### Autenticación (`/api/v1/auth`)
- `POST /sign-up`: Registrar usuario
- `POST /sign-in`: Iniciar sesión
- `POST /sign-out`: Cerrar sesión
- `GET /session`: Obtener sesión actual
- `POST /verify-email`: Verificar email
- `POST /resend-verification`: Reenviar código
- `POST /forgot-password`: Solicitar reset
- `POST /reset-password`: Resetear password
- `GET /oauth/{provider}`: OAuth flow (placeholder)
- `GET /oauth/{provider}/callback`: OAuth callback (placeholder)
- `GET /users/me`: Info del usuario actual
- `DELETE /sessions/cleanup`: Limpiar sesiones (admin)

### 🚀 Mejoras de arquitectura

- Patrón MVC consistente en todo el proyecto
- Separación de responsabilidades (schemas, services, endpoints)
- Async/await en todas las operaciones de base de datos
- Manejo robusto de errores con HTTPException
- Logging mejorado en todas las operaciones críticas
- Dependency injection con FastAPI

### 📦 Dependencias nuevas

```
motor==3.3.2                    # MongoDB async driver
pymongo==4.6.1                  # MongoDB sync driver
passlib[bcrypt]==1.7.4          # Password hashing
bcrypt==4.1.2                   # Bcrypt algorithm
PyJWT==2.8.0                    # JWT tokens
python-jose[cryptography]==3.3.0 # Additional crypto
pytest-asyncio==0.21.1          # Async testing
```

### 🔄 Migración

Para actualizar desde v1.0.0:

1. Instalar nuevas dependencias:
   ```bash
   pip install -r requirements.txt
   ```

2. Configurar MongoDB:
   ```bash
   # Local
   mongod
   
   # O usar MongoDB Atlas (cloud)
   ```

3. Actualizar `.env`:
   ```bash
   cp .env.example .env
   # Editar con tus valores
   ```

4. Ejecutar servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

### ⚠️ Breaking Changes

- El servidor ahora requiere MongoDB para iniciar
- Nuevas variables de entorno obligatorias:
  - `MONGODB_URL`
  - `DATABASE_NAME`
  - `JWT_SECRET_KEY`
  - `SMTP_*` (para emails)

### 🎉 Próximos pasos (v2.1.0)

- [ ] OAuth completo con Google y GitHub
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] 2FA (Two-Factor Authentication)
- [ ] Admin panel para gestión de usuarios
- [ ] Logs de auditoría

---

## [2025-11-25] - Soporte para archivos Excel

### ✨ Nuevas características
- **Soporte para archivos XLSX/XLS**: Ahora el sistema acepta archivos de Excel además de CSV
  - Formatos soportados: `.csv`, `.xlsx`, `.xls`
  - Validación automática de extensiones en el endpoint de upload
  - Detección automática del formato de archivo para procesamiento

### 🔧 Cambios técnicos
- **TradeParserService**:
  - Renombrado: `load_trades_from_csv()` → `load_trades_from_file()`
  - Agregada detección automática de extensión de archivo
  - Uso de `pd.read_excel()` con engine `openpyxl` para archivos Excel
  
- **Analytics API**:
  - Actualizado endpoint `/upload-trades` con validación de extensiones
  - Todos los endpoints ahora buscan archivos `.csv`, `.xlsx`, y `.xls`
  - Mensajes de error más descriptivos

### 📦 Dependencias
- Ya incluye `openpyxl==3.1.2` en requirements.txt

### 🚀 Uso
```python
# Ahora puedes subir tanto CSV como Excel
POST /api/v1/analytics/upload-trades
Content-Type: multipart/form-data

file: operaciones_mt5.xlsx  # ✅ Ahora funciona!
file: operaciones_mt5.csv   # ✅ También funciona!
```

