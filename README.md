# 🚀 Trading Bot Backend API

Sistema profesional de análisis de operaciones de trading con autenticación completa y gestión de usuarios. Backend construido con **FastAPI** + **MongoDB** para procesar datos históricos de MT5 y calcular métricas analíticas avanzadas.

## 📋 Características

### 🔐 Sistema de Autenticación (Auth Service)
- ✅ **Registro y Login**: Sign-up/Sign-in con email y password
- ✅ **Gestión de Sesiones**: JWT tokens con MongoDB
- ✅ **Verificación de Email**: Código de 6 dígitos con templates profesionales
- ✅ **Recuperación de Contraseña**: Flow completo de password reset
- ✅ **Seguridad**: Bcrypt para passwords, JWT para tokens
- ✅ **OAuth Ready**: Estructura preparada para Google y GitHub
- ✅ **Roles de Usuario**: User, Trader, Admin

### 📊 Análisis Profesional de Trading
- ✅ **KPIs Completos**: Win rate, Profit Factor, Payoff Ratio, Drawdown
- ✅ **Análisis por Símbolo**: Estadísticas desglosadas por par (EURUSD, GBPUSD, etc)
- ✅ **Series Temporales**: Curva de capital, profit diario/mensual
- ✅ **Análisis de Rachas**: Mayor racha ganadora/perdedora
- ✅ **Heatmaps**: Rentabilidad por hora del día
- ✅ **Distribuciones**: Histogramas de ganancias y duraciones

---

## 🏗️ Arquitectura

### Patrón MVC (Modelo-Vista-Controlador)

```
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│                                                          │
│  ┌────────────────┐  ┌────────────────┐                │
│  │  Auth Service  │  │ Analytics Srvc │                │
│  │  (Microserv.)  │  │                │                │
│  └────────┬───────┘  └────────┬───────┘                │
│           │                   │                          │
│  ┌────────▼───────────────────▼───────┐                │
│  │         MongoDB Database            │                │
│  │  - users, sessions, trades, etc.    │                │
│  └─────────────────────────────────────┘                │
└──────────────────────────────────────────────────────────┘
```

### Tecnologías

- **Framework**: FastAPI 0.104+
- **Database**: MongoDB (Motor async driver)
- **Authentication**: JWT + bcrypt
- **Data Processing**: Pandas, NumPy
- **Email**: SMTP (Gmail, SendGrid, Mailgun)
- **Server**: Uvicorn (ASGI)

---

## 📁 Estructura del Proyecto

```
trading-bot-backend/
├── app/
│   ├── main.py                         # FastAPI app principal
│   │
│   ├── api/v1/endpoints/
│   │   ├── auth.py                     # 🔐 Auth endpoints
│   │   └── analytics.py                # 📊 Analytics endpoints
│   │
│   ├── services/
│   │   ├── auth_service.py             # Lógica de autenticación
│   │   ├── analytics_service.py        # Cálculo de KPIs
│   │   └── trade_parser_service.py     # Parser CSV/XLSX
│   │
│   ├── schemas/
│   │   ├── auth.py                     # Modelos de autenticación
│   │   ├── trade.py                    # Modelo Trade
│   │   └── analytics.py                # Modelo Analytics
│   │
│   ├── config/
│   │   └── database.py                 # Conexión MongoDB
│   │
│   └── utils/
│       ├── security.py                 # Hash, JWT, tokens
│       └── email.py                    # Envío de emails
│
├── data/
│   ├── raw/                            # CSV originales
│   ├── processed/                      # Datos procesados
│   └── cache/                          # KPIs cacheados
│
├── tests/
│   ├── test_auth.py
│   └── test_analytics.py
│
├── .env.example                        # Variables de entorno
├── requirements.txt                    # Dependencias
├── README.md                           # Este archivo
└── AUTH-SERVICE-IMPLEMENTACION.md      # Documentación detallada
```

---

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd trading-bot-backend
```

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=trading_bot_db

# JWT Security
JWT_SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 días

# Email (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 5. Configurar MongoDB

**Opción A: MongoDB Local**
```bash
# Instalar MongoDB Community Edition
# https://www.mongodb.com/try/download/community

# Iniciar servicio
mongod
```

**Opción B: MongoDB Atlas (Cloud - Recomendado)**
1. Crear cuenta en [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crear cluster gratuito (M0)
3. Obtener connection string
4. Actualizar `MONGODB_URL` en `.env`

### 6. Configurar Email

**Para Gmail:**
1. Habilitar 2FA en tu cuenta de Google
2. Generar App Password: https://myaccount.google.com/apppasswords
3. Usar el password generado en `SMTP_PASSWORD`

**Para otros servicios:**
- SendGrid: https://sendgrid.com/
- Mailgun: https://www.mailgun.com/
- AWS SES: https://aws.amazon.com/ses/

---

## ▶️ Ejecutar el Servidor

```bash
# Opción 1: Uvicorn directo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Python module
python -m app.main
```

El servidor estará disponible en: http://localhost:8000

---

## 📖 Documentación API

Una vez iniciado el servidor, accede a:

- **Swagger UI** (interactivo): http://localhost:8000/docs
- **ReDoc** (documentación): http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🔑 Endpoints Principales

### Autenticación (`/api/v1/auth`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/sign-up` | Registrar nuevo usuario |
| POST | `/sign-in` | Iniciar sesión |
| POST | `/sign-out` | Cerrar sesión |
| GET | `/session` | Obtener sesión actual |
| POST | `/verify-email` | Verificar email con código |
| POST | `/resend-verification` | Reenviar código de verificación |
| POST | `/forgot-password` | Solicitar reset de password |
| POST | `/reset-password` | Resetear password con token |
| GET | `/oauth/{provider}` | Iniciar OAuth (Google/GitHub) |

### Analytics (`/api/v1/analytics`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/upload-trades` | Subir CSV/XLSX de MT5 |
| GET | `/trades` | Listar operaciones |
| GET | `/summary` | Resumen KPIs completo |
| GET | `/filter` | Filtrar operaciones |
| GET | `/timeseries` | Series temporales |
| GET | `/by-symbol` | Stats por símbolo |
| GET | `/hourly-heatmap` | Heatmap horario |
| GET | `/daily-stats` | Estadísticas diarias |
| GET | `/monthly-stats` | Estadísticas mensuales |

---

## 💡 Ejemplos de Uso

### 1. Registrar Usuario

```bash
curl -X POST "http://localhost:8000/api/v1/auth/sign-up" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "password": "SecurePass123",
    "name": "John Trader"
  }'
```

### 2. Verificar Email

```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "code": "123456"
  }'
```

### 3. Iniciar Sesión

```bash
curl -X POST "http://localhost:8000/api/v1/auth/sign-in" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "trader@example.com",
    "password": "SecurePass123"
  }'
```

### 4. Subir Operaciones (Con Token)

```bash
curl -X POST "http://localhost:8000/api/v1/analytics/upload-trades" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data/raw/trades.csv"
```

### 5. Obtener Resumen Analítico

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Formato CSV de MT5

El archivo CSV debe contener estas columnas:

**Español:**
```
Hora de apertura, Hora de cierre, Símbolo, Tipo, Volumen, 
Precio de apertura, Precio de cierre, Ganancias, Comente
```

**Inglés:**
```
Open Time, Close Time, Symbol, Type, Volume, 
Open Price, Close Price, Profit, Comment
```

**Ejemplo:**
```csv
Open Time,Close Time,Symbol,Type,Volume,Open Price,Close Price,Profit,Comment
2025-01-15 09:30:00,2025-01-15 10:45:00,EURUSD,BUY,1.0,1.0850,1.0870,200.0,SMA Crossover
2025-01-15 14:00:00,2025-01-15 15:30:00,GBPUSD,SELL,0.5,1.2650,1.2620,150.0,RSI Signal
```

---

## 🔒 Seguridad

### Implementado

✅ Password hashing con bcrypt  
✅ JWT tokens con expiración  
✅ Sesiones en MongoDB  
✅ Email verification  
✅ Password reset flow  
✅ CORS configurado  
✅ HTTPS ready  

### Recomendaciones para Producción

1. **Cambiar JWT_SECRET_KEY** a un valor aleatorio y seguro
2. **Usar HTTPS** (SSL/TLS certificates)
3. **Configurar CORS** con dominios específicos (no usar `*`)
4. **Rate Limiting** para prevenir abuse
5. **Usar servicios SMTP profesionales** (SendGrid, Mailgun)
6. **Implementar 2FA** (Two-Factor Authentication)
7. **Logs de auditoría** para acciones críticas
8. **Backups automáticos** de MongoDB

---

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Con coverage
pytest --cov=app tests/

# Tests específicos
pytest tests/test_auth.py -v
```

---

## 📦 Dependencias Principales

```
fastapi==0.104.1           # Framework web
uvicorn==0.24.0            # ASGI server
motor==3.3.2               # MongoDB async driver
passlib[bcrypt]==1.7.4     # Password hashing
PyJWT==2.8.0               # JWT tokens
pandas==2.1.3              # Data processing
numpy==1.26.2              # Numerical computing
```

Ver `requirements.txt` para la lista completa.

---

## 🗂️ Base de Datos

### Colecciones de MongoDB

1. **users** - Información de usuarios
   - email (unique), password_hash, name, role, email_verified

2. **sessions** - Sesiones activas
   - user_id, token, expires_at

3. **verifications** - Códigos de verificación
   - identifier, code, expires_at

4. **accounts** - Cuentas OAuth
   - user_id, provider, provider_id

5. **trades** - Operaciones de trading (futuro)
   - user_id, symbol, type, profit, etc.

---

## 🎯 Roadmap

### Fase 1 (Completada) ✅
- [x] Sistema de autenticación completo
- [x] Análisis de operaciones
- [x] Upload de CSV/XLSX
- [x] KPIs profesionales

### Fase 2 (En Progreso) 🚧
- [ ] OAuth con Google y GitHub
- [ ] Refresh tokens
- [ ] Rate limiting
- [ ] 2FA (Two-Factor Authentication)

### Fase 3 (Próximamente) 📋
- [ ] Live trading integration
- [ ] Real-time WebSocket updates
- [ ] Background jobs con Celery
- [ ] Redis caching
- [ ] Machine Learning para patrones
- [ ] Mobile app (React Native)

---

## 📝 Licencia

MIT License - Ver LICENSE file para detalles

---

## 👨‍💻 Autor

**Harry El Trader**  
Trading Portfolio Analytics System  

- GitHub: [@harryeltrader](https://github.com/harryeltrader)
- Email: contact@harryeltrader.com

---

## 🤝 Contribuir

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📚 Documentación Adicional

- [AUTH-SERVICE-IMPLEMENTACION.md](AUTH-SERVICE-IMPLEMENTACION.md) - Documentación detallada del Auth Service
- [CHANGELOG.md](CHANGELOG.md) - Historial de cambios
- [API Documentation](http://localhost:8000/docs) - Swagger UI interactiva

---

## ❓ FAQ

**Q: ¿Cómo obtengo un App Password de Gmail?**  
A: Habilita 2FA y ve a https://myaccount.google.com/apppasswords

**Q: ¿Puedo usar PostgreSQL en lugar de MongoDB?**  
A: Sí, el proyecto tiene soporte para SQLAlchemy (ver requirements.txt)

**Q: ¿Cómo cambio el tiempo de expiración del token?**  
A: Modifica `ACCESS_TOKEN_EXPIRE_MINUTES` en `.env`

**Q: ¿El sistema soporta múltiples idiomas?**  
A: Actualmente solo español/inglés. i18n está en el roadmap.

---

## 🆘 Soporte

¿Necesitas ayuda?

1. Revisa la [documentación completa](http://localhost:8000/docs)
2. Lee [AUTH-SERVICE-IMPLEMENTACION.md](AUTH-SERVICE-IMPLEMENTACION.md)
3. Abre un [issue en GitHub](https://github.com/harryeltrader/trading-bot-backend/issues)
4. Contacta: support@harryeltrader.com

---

**⭐ Si este proyecto te fue útil, dale una estrella en GitHub!**

---

Desarrollado con ❤️ por Harry El Trader | © 2025
