# Trading Bot Backend - FastAPI + MT5

Production-ready backend architecture for algorithmic trading with MetaTrader 5 and CCXT integration. Fully structured with professional code organization, WebSocket real-time updates, strategy management, and comprehensive REST API endpoints.

## Project Structure

```
trading-bot-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Environment configuration
│   │   ├── security.py            # JWT, CORS, middleware
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── account.py           # Account info endpoints
│   │   │   │   ├── rates.py             # OHLCV data endpoints
│   │   │   │   ├── orders.py            # Order management
│   │   │   │   ├── positions.py         # Position management
│   │   │   │   ├── strategies.py        # Strategy control
│   │   │   │   ├── backtest.py          # Backtesting endpoints
│   │   │   │   ├── health.py            # Health check
│   ├── services/
│   │   ├── mt5service.py         # MT5 connection logic
│   │   ├── ccxtservice.py        # CCXT integration
│   │   ├── strategyservice.py    # Strategy orchestration
│   │   ├── backtestservice.py    # Backtesting logic
│   ├── models/
│   │   ├── account.py
│   │   ├── order.py
│   │   ├── strategy.py
│   ├─┐ schemas/
│   │   ├── account.py           # Pydantic schemas
│   │   ├── order.py
│   │   ├─┐ strategy.py
│   ├── connectors/
│   │   ├── base.py              # Base broker interface
│   │   ├── mt5connector.py       # MT5 implementation
│   │   ├─┐ ccxtconnector.py      # CCXT implementation
│   ├── indicators/
│   │   ├── technical.py         # SMA, EMA, RSI, MACD
│   │   ├─┐ custom.py            # Custom indicators
│   ├── strategies/
│   │   ├── basestrategy.py      # Base strategy class
│   │   ├── smacrossover.py      # SMA crossover strategy
│   │   ├─┐ rsistrategy.py       # RSI strategy
│   ├── websocket/
│   │   ├── handlers.py          # WebSocket handlers
│   ├── utils/
│   │   ├── logger.py            # Logging setup
│   │   ├─┐ helpers.py           # Helper functions
│   ├── database/
│   │   ├── database.py          # Database configuration
│   │   ├─┐ models.py            # ORM models
│   ├── tests/
│   │   ├── test_account.py
│   │   ├── test_orders.py
│   │   ├─┐ test_strategies.py
├── .env.example
├── .gitignore
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── run.py
└── README.md
```

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/tu-usuario/trading-bot-backend.git
cd trading-bot-backend
```

### 2. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # MacOS/Linux
venv\\Scripts\\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```
FASTAPI_ENV=development
DEBUG=true

# MT5 Configuration
MT5_LOGIN=123456
MT5_PASSWORD=your_password
MT5_SERVER=broker-server
MT5_TIMEOUT=30

# CCXT Configuration (Optional)
CCXT_EXCHANGE=binance
CCXT_API_KEY=your_api_key
CCXT_API_SECRET=your_api_secret

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./tradingbot.db

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 4. Run Server

```bash
python run.py
# Or directly:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Dependencies

**Core Framework:**
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.0.0
- pydantic-settings==2.0.0

**MT5 & Broker Connectivity:**
- metatrader5==5.0.45
- ccxt==4.0.0
- requests==2.31.0
- websocket-client==1.6.0

**Data Analysis:**
- pandas==2.0.0
- numpy==1.24.0
- ta-lib==0.4.27

**Database:**
- sqlalchemy==2.0.0
- psycopg2-binary==2.9.0
- alembic==1.12.0

**Authentication:**
- python-jose==3.3.0
- passlib==1.7.4
- python-multipart==0.0.6

**WebSocket:**
- python-socketio==5.9.0
- python-socketio[asyncio_manager]==5.9.0

**Utilities:**
- python-dotenv==1.0.0
- python-dateutil==2.8.2
- pytz==2023.3

**Testing:**
- pytest==7.4.0
- pytest-asyncio==0.21.0

**Development:**
- black==23.11.0
- flake8==6.1.0
- mypy==1.7.0

## API Endpoints (MVP)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/account` | Get account info |
| GET | `/api/v1/positions` | Get open positions |
| GET | `/api/v1/rates?symbol=EURUSD&timeframe=3600&count=100` | Get OHLCV data |
| POST | `/api/v1/orders/buy` | Create buy order |
| POST | `/api/v1/orders/sell` | Create sell order |
| GET | `/api/v1/strategies` | List strategies |
| POST | `/api/v1/strategies/start` | Start strategy |

## Architecture Highlights

**Clean Code Structure:**
- Separation of concerns (services, connectors, models)
- Dependency injection pattern
- Type hints throughout
- Comprehensive error handling

**Real-time Updates:**
- WebSocket support for live price feeds
- Event-driven strategy execution
- Async/await for non-blocking operations

**Professional Features:**
- JWT authentication
- CORS configuration
- Request validation with Pydantic
- Structured logging
- Database ORM with SQLAlchemy

**Broker Integration:**
- MetaTrader 5 connector
- CCXT for crypto exchanges
- Pluggable broker interface

## Next Steps

- [ ] Complete order management endpoints
- [ ] Implement SMA and RSI trading strategies
- [ ] Add WebSocket real-time price updates
- [ ] Integrate PostgreSQL database
- [ ] Add comprehensive unit tests
- [ ] Complete API documentation
- [ ] Setup Docker deployment

## GitHub Setup

1. Create empty repository on GitHub: `trading-bot-backend`
2. Clone this project
3. Change remote:

```bash
git remote set-url origin https://github.com/tu-usuario/trading-bot-backend.git
git push -u origin main
```

## License

MIT License - Feel free to use and modify for your trading projects.
