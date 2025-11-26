# 🚀 Trading Portfolio Analytics Backend

Sistema profesional de análisis de operaciones de trading similar a MyFxBook. Backend construido con FastAPI para procesar datos históricos de MT5 y calcular métricas analíticas avanzadas.

## 📋 Características

### Análisis Profesional de Trading
- ✅ **KPIs Completos**: Win rate, Profit Factor, Payoff Ratio, Drawdown
- ✅ **Análisis por Símbolo**: Estadísticas desglosadas por par (EURUSD, GBPUSD, etc)
- ✅ **Series Temporales**: Curva de capital, profit diario/mensual
- ✅ **Análisis de Rachas**: Mayor racha ganadora/perdedora
- ✅ **Heatmaps**: Rentabilidad por hora del día
- ✅ **Distribuciones**: Histogramas de ganancias y duraciones

### Endpoints API

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/analytics/upload-trades` | Subir CSV de operaciones |
| GET | `/api/v1/analytics/trades` | Listar todas las operaciones |
| GET | `/api/v1/analytics/summary` | Resumen KPIs completo |
| GET | `/api/v1/analytics/filter` | Filtrar operaciones |
| GET | `/api/v1/analytics/timeseries` | Series temporales |
| GET | `/api/v1/analytics/by-symbol` | Stats por par |
| GET | `/api/v1/analytics/hourly-heatmap` | Rentabilidad por hora |
| GET | `/api/v1/analytics/daily-stats` | Stats diarios |
| GET | `/api/v1/analytics/monthly-stats` | Stats mensuales |

## 🏗️ Estructura del Proyecto

```
trading-bot-backend/
├── app/
│   ├── main.py                          # FastAPI app principal
│   ├── api/v1/endpoints/
│   │   └── analytics.py                 # Endpoints de analytics
│   ├── services/
│   │   ├── trade_parser_service.py      # Parser CSV
│   │   └── analytics_service.py         # Cálculo de KPIs
│   └── schemas/
│       ├── trade.py                     # Modelo Trade
│       └── analytics.py                 # Modelo Analytics
├── data/
│   ├── raw/                             # CSV originales
│   │   └── sample_trades.csv            # Datos de ejemplo
│   ├── processed/                       # Datos procesados
│   └── cache/                           # KPIs cacheados
├── tests/
│   └── test_analytics.py                # Tests
├── requirements.txt                     # Dependencias
└── .env.example                         # Variables de entorno
```

## 🚀 Instalación y Uso

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env
# Editar .env si es necesario
```

### 3. Ejecutar el Servidor

```bash
# Opción 1: Usando uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Usando Python
python -m app.main
```

### 4. Acceder a la Documentación

Una vez iniciado el servidor, accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Uso del Sistema

### 1. Subir Archivo CSV de MT5

```bash
curl -X POST "http://localhost:8000/api/v1/analytics/upload-trades" \
  -F "file=@data/raw/sample_trades.csv"
```

O usar la interfaz Swagger en `/docs`

### 2. Obtener Resumen Analítico

```bash
curl "http://localhost:8000/api/v1/analytics/summary"
```

Respuesta ejemplo:
```json
{
  "total_trades": 150,
  "winning_trades": 95,
  "losing_trades": 50,
  "break_even": 5,
  "win_rate": 63.33,
  "profit_factor": 2.15,
  "total_profit": 15000.50,
  "max_drawdown": -2500.0,
  "best_day": "2025-01-15",
  "equity_curve": [200, 250, 100, ...],
  "symbol_stats": {
    "EURUSD": {
      "trades": 80,
      "profit": 8500.0,
      "win_rate": 65.0
    }
  }
}
```

### 3. Filtrar Operaciones

```bash
# Por símbolo
curl "http://localhost:8000/api/v1/analytics/filter?symbol=EURUSD"

# Por estado
curl "http://localhost:8000/api/v1/analytics/filter?status=GANADOR"

# Combinado
curl "http://localhost:8000/api/v1/analytics/filter?symbol=EURUSD&status=GANADOR&min_profit=100"
```

### 4. Obtener Estadísticas por Símbolo

```bash
curl "http://localhost:8000/api/v1/analytics/by-symbol"
```

### 5. Heatmap Horario

```bash
curl "http://localhost:8000/api/v1/analytics/hourly-heatmap"
```

## 📝 Formato CSV de MT5

El archivo CSV debe contener las siguientes columnas (en español o inglés):

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
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Con coverage
pytest --cov=app tests/
```

## 📦 Dependencias Principales

- **FastAPI**: Framework web moderno y rápido
- **Pandas**: Procesamiento de datos
- **NumPy**: Cálculos numéricos
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

## 🎯 Próximas Características (Fase 2)

- [ ] PostgreSQL + SQLAlchemy ORM
- [ ] Caching con Redis
- [ ] WebSocket para updates real-time
- [ ] Background jobs con Celery
- [ ] OAuth con MT5 API
- [ ] Exportación a PDF/Excel
- [ ] Comparación de estrategias
- [ ] Machine Learning para patrones

## 📄 Licencia

MIT

## 👨‍💻 Autor

Harry El Trader - Trading Portfolio Analytics System

---

**¿Necesitas ayuda?** Abre un issue o consulta la documentación en `/docs`
