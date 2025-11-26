# 📋 PLAN DE DESARROLLO COMPLETO: Trading Portfolio Analytics

## Sistema: Análisis Profesional de Operaciones (Similar a MyFxBook)
**Stack:** FastAPI Backend + Vue 3/Nuxt 3 Frontend + MT5
**Fecha:** Nov 25, 2025
**Versión:** 1.0 Plan Técnico

---

# 🎯 OBJETIVOS GENERALES

1. **Backend:** Procesar datos históricos de operaciones MT5 y calcular métricas analíticas profesionales
2. **Frontend:** Visualizar dashboard interactivo con gráficos, tablas y estadísticas tipo MyFxBook
3. **Datos:** Excel/CSV exportados desde MT5 como fuente inicial
4. **Escalabilidad:** Preparado para API OAuth/WebSocket en futuro

---

# PARTE 1: PLAN DE BACKEND (FastAPI)

## 1.1 Datos de Entrada

### Fuente Primaria: Exportación MT5 (Excel/CSV)

**Columnas esperadas del archivo exportado:**
```
Open Time | Symbol | Order Type | Volume | Open Price | Close Price | 
Profit $ | Profit % | Comment | Close Time | Duration | Spread
```

**Ubicación sugerida en proyecto:**
```
trading-bot-backend/
├── data/
│   ├── raw/
│   │   └── operaciones_mt5.csv          (Archivo exportado original)
│   ├── processed/
│   │   └── operaciones_procesadas.json  (Datos ya procesados)
│   └── cache/
│       └── kpis_cache.json              (KPIs cacheados)
├── services/
│   ├── trade_parser_service.py          (Parsear CSV)
│   └── analytics_service.py             (Calcular KPIs)
└── schemas/
    ├── trade.py                         (Modelo Trade)
    └── analytics.py                     (Modelos Analytics)
```

---

## 1.2 Modelos de Datos (Pydantic Schemas)

### Trade Model (Operación Individual)

```python
# app/schemas/trade.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Trade(BaseModel):
    id: int                          # ID único
    open_time: datetime              # Hora apertura
    close_time: datetime             # Hora cierre
    symbol: str                      # Par (EURUSD, GBPUSD, etc)
    order_type: str                  # BUY, SELL
    volume: float                    # Lotes
    open_price: float                # Precio apertura
    close_price: float               # Precio cierre
    profit_usd: float                # P&L en $
    profit_pct: float                # P&L %
    duration: int                    # Duración en minutos
    spread: Optional[float]          # Spread en pips
    comment: Optional[str]           # Comentario/nota
    status: str                      # GANADOR, PERDEDOR, BREAK_EVEN
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "open_time": "2025-01-15T09:30:00",
                "close_time": "2025-01-15T10:45:00",
                "symbol": "EURUSD",
                "order_type": "BUY",
                "volume": 1.0,
                "open_price": 1.0850,
                "close_price": 1.0870,
                "profit_usd": 200.0,
                "profit_pct": 0.184,
                "duration": 75,
                "spread": 1.2,
                "comment": "SMA Crossover signal",
                "status": "GANADOR"
            }
        }
```

### KPI Analytics Model

```python
# app/schemas/analytics.py

from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class DailyStats(BaseModel):
    date: str                        # YYYY-MM-DD
    trades: int                      # Operaciones ese día
    profit: float                    # P&L neto
    win_rate: float                  # % operaciones ganadoras
    max_loss: float                  # Mayor pérdida del día

class MonthlyStats(BaseModel):
    month: str                       # YYYY-MM
    trades: int
    profit: float
    win_rate: float
    best_day: str
    worst_day: str

class Analytics(BaseModel):
    # RESUMEN GENERAL
    total_trades: int                # Total de operaciones
    winning_trades: int              # Operaciones ganadoras
    losing_trades: int               # Operaciones perdedoras
    break_even: int                  # Break even
    
    # PROFIT & LOSS
    total_profit: float              # Ganancia/pérdida total $
    total_profit_pct: float          # Ganancia/pérdida %
    average_profit: float            # Profit promedio por trade
    
    # RATIOS
    win_rate: float                  # % de operaciones ganadoras
    profit_factor: float             # (Ganancias totales / Pérdidas totales)
    payoff_ratio: float              # (Ganancia promedio / Pérdida promedio)
    
    # DRAWDOWN
    max_drawdown: float              # Drawdown máximo $
    max_drawdown_pct: float          # Drawdown máximo %
    current_drawdown: float          # Drawdown actual $
    
    # RACHA
    longest_win_streak: int          # Mayor racha ganadora
    longest_loss_streak: int         # Mayor racha perdedora
    current_streak: int              # Racha actual (+ ganador, - perdedor)
    
    # ESTADÍSTICAS DE PARES
    symbol_stats: Dict[str, Dict]    # Stats por par (EURUSD, GBPUSD, etc)
    
    # ESTADÍSTICAS POR DÍA
    best_day: str                    # Día con mayor ganancia
    best_day_profit: float
    worst_day: str                   # Día con mayor pérdida
    worst_day_profit: float
    
    # ESTADÍSTICAS POR HORA
    best_hour: int                   # Hora más rentable (0-23)
    best_hour_profit: float
    
    # CURVA DE CAPITAL / EQUITY
    equity_curve: List[float]        # Progresión de capital
    equity_dates: List[str]          # Fechas correspondientes
    
    # DISTRIBUCIONES
    profit_distribution: Dict        # Histograma P&L
    duration_distribution: Dict      # Distribución de duraciones
    
    # SERIES TEMPORALES
    daily_stats: List[DailyStats]
    monthly_stats: List[MonthlyStats]
    
    # METADATA
    period_start: str                # Primera operación
    period_end: str                  # Última operación
    total_days: int                  # Días activos
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_trades": 150,
                "winning_trades": 95,
                "win_rate": 0.633,
                "total_profit": 15000.50,
                "max_drawdown": -2500.0,
                "best_day": "2025-01-15",
                # ... más campos
            }
        }
```

---

## 1.3 Servicios Backend (Lógica Principal)

### 1.3.1 Trade Parser Service

```python
# app/services/trade_parser_service.py

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict
from app.schemas.trade import Trade

logger = logging.getLogger(__name__)

class TradeParserService:
    """Parsear operaciones desde CSV exportado de MT5"""
    
    @staticmethod
    def load_trades_from_csv(file_path: str) -> List[Trade]:
        """Cargar operaciones desde archivo CSV"""
        try:
            # Leer CSV (ajustar separadores según tu export)
            df = pd.read_csv(file_path, encoding='utf-8')
            
            # Renombrar columnas si es necesario (MT5 export usa idioma local)
            column_mapping = {
                'Hora de apertura': 'open_time',
                'Hora de cierre': 'close_time',
                'Símbolo': 'symbol',
                'Tipo': 'order_type',
                'Volumen': 'volume',
                'Precio de apertura': 'open_price',
                'Precio de cierre': 'close_price',
                'Ganancias': 'profit_usd',
                'Comente': 'comment'
            }
            df.rename(columns=column_mapping, inplace=True)
            
            trades = []
            for idx, row in df.iterrows():
                trade = Trade(
                    id=idx,
                    open_time=pd.to_datetime(row['open_time']),
                    close_time=pd.to_datetime(row['close_time']),
                    symbol=row['symbol'].strip(),
                    order_type=row['order_type'].upper(),
                    volume=float(row['volume']),
                    open_price=float(row['open_price']),
                    close_price=float(row['close_price']),
                    profit_usd=float(row['profit_usd']),
                    profit_pct=(float(row['profit_usd']) / abs(float(row['open_price']) * float(row['volume']) * 100)) * 100,
                    duration=int((pd.to_datetime(row['close_time']) - pd.to_datetime(row['open_time'])).total_seconds() / 60),
                    comment=row.get('comment', ''),
                    status='GANADOR' if float(row['profit_usd']) > 0 else ('PERDEDOR' if float(row['profit_usd']) < 0 else 'BREAK_EVEN')
                )
                trades.append(trade)
            
            logger.info(f"✅ Cargadas {len(trades)} operaciones desde {file_path}")
            return trades
            
        except Exception as e:
            logger.error(f"❌ Error cargando CSV: {e}")
            raise

    @staticmethod
    def validate_trade_data(trades: List[Trade]) -> bool:
        """Validar integridad de datos"""
        if not trades:
            logger.warning("⚠️ No hay operaciones para validar")
            return False
        
        logger.info(f"✅ Validadas {len(trades)} operaciones")
        return True
```

### 1.3.2 Analytics Service (Cálculo de KPIs)

```python
# app/services/analytics_service.py

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from app.schemas.trade import Trade
from app.schemas.analytics import Analytics, DailyStats, MonthlyStats

class AnalyticsService:
    """Calcular KPIs y estadísticas de operaciones"""
    
    @staticmethod
    def calculate_all_analytics(trades: List[Trade]) -> Analytics:
        """Calcular todas las métricas analíticas"""
        
        df = pd.DataFrame([t.dict() for t in trades])
        df['open_time'] = pd.to_datetime(df['open_time'])
        df['close_time'] = pd.to_datetime(df['close_time'])
        df = df.sort_values('open_time')
        
        # CÁLCULOS GENERALES
        total_trades = len(df)
        winning = len(df[df['profit_usd'] > 0])
        losing = len(df[df['profit_usd'] < 0])
        break_even = len(df[df['profit_usd'] == 0])
        
        total_profit = df['profit_usd'].sum()
        win_rate = (winning / total_trades * 100) if total_trades > 0 else 0
        
        # PROFIT FACTOR
        gains = df[df['profit_usd'] > 0]['profit_usd'].sum()
        losses = abs(df[df['profit_usd'] < 0]['profit_usd'].sum())
        profit_factor = (gains / losses) if losses > 0 else 0
        
        # PAYOFF RATIO
        avg_win = df[df['profit_usd'] > 0]['profit_usd'].mean() if winning > 0 else 0
        avg_loss = abs(df[df['profit_usd'] < 0]['profit_usd'].mean()) if losing > 0 else 1
        payoff_ratio = avg_win / avg_loss if avg_loss > 0 else 0
        
        # DRAWDOWN
        cumsum = df['profit_usd'].cumsum()
        running_max = cumsum.cummax()
        drawdown = cumsum - running_max
        max_drawdown = drawdown.min()
        max_drawdown_pct = (max_drawdown / running_max.max() * 100) if running_max.max() > 0 else 0
        
        # RACHAS
        df['sign'] = np.sign(df['profit_usd'])
        df['streak_group'] = (df['sign'] != df['sign'].shift()).cumsum()
        streaks = df.groupby('streak_group').size()
        longest_win = streaks[df.groupby('streak_group')['profit_usd'].sum() > 0].max() if any(df.groupby('streak_group')['profit_usd'].sum() > 0) else 0
        longest_loss = streaks[df.groupby('streak_group')['profit_usd'].sum() < 0].max() if any(df.groupby('streak_group')['profit_usd'].sum() < 0) else 0
        
        # MEJOR/PEOR DÍA
        daily = df.groupby(df['open_time'].dt.date)['profit_usd'].sum()
        best_day = daily.idxmax()
        best_day_profit = daily.max()
        worst_day = daily.idxmin()
        worst_day_profit = daily.min()
        
        # MEJOR HORA
        df['hour'] = df['open_time'].dt.hour
        hourly = df.groupby('hour')['profit_usd'].mean()
        best_hour = hourly.idxmax()
        best_hour_profit = hourly.max()
        
        # ESTADÍSTICAS POR SÍMBOLO
        symbol_stats = {}
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol]
            symbol_stats[symbol] = {
                'trades': len(symbol_df),
                'profit': float(symbol_df['profit_usd'].sum()),
                'win_rate': float((len(symbol_df[symbol_df['profit_usd'] > 0]) / len(symbol_df) * 100) if len(symbol_df) > 0 else 0),
                'avg_profit': float(symbol_df['profit_usd'].mean())
            }
        
        # CURVA DE CAPITAL
        equity_curve = [float(x) for x in cumsum.values]
        equity_dates = [d.isoformat() for d in df['open_time']]
        
        # ESTADÍSTICAS DIARIAS
        daily_stats = []
        for date, group in df.groupby(df['open_time'].dt.date):
            daily_stats.append(DailyStats(
                date=str(date),
                trades=len(group),
                profit=float(group['profit_usd'].sum()),
                win_rate=float((len(group[group['profit_usd'] > 0]) / len(group) * 100) if len(group) > 0 else 0),
                max_loss=float(group['profit_usd'].min())
            ))
        
        # CONSTRUIR OBJETO ANALYTICS
        analytics = Analytics(
            total_trades=total_trades,
            winning_trades=winning,
            losing_trades=losing,
            break_even=break_even,
            total_profit=total_profit,
            total_profit_pct=float((total_profit / abs(df['open_price'].iloc[0] * df['volume'].iloc[0])) * 100) if len(df) > 0 else 0,
            average_profit=float(df['profit_usd'].mean()),
            win_rate=float(win_rate),
            profit_factor=float(profit_factor),
            payoff_ratio=float(payoff_ratio),
            max_drawdown=float(max_drawdown),
            max_drawdown_pct=float(max_drawdown_pct),
            current_drawdown=float(drawdown.iloc[-1]) if len(drawdown) > 0 else 0,
            longest_win_streak=int(longest_win),
            longest_loss_streak=int(longest_loss),
            current_streak=int(df['sign'].iloc[-1] if len(df) > 0 else 0),
            symbol_stats=symbol_stats,
            best_day=str(best_day),
            best_day_profit=float(best_day_profit),
            worst_day=str(worst_day),
            worst_day_profit=float(worst_day_profit),
            best_hour=int(best_hour),
            best_hour_profit=float(best_hour_profit),
            equity_curve=equity_curve,
            equity_dates=equity_dates,
            daily_stats=daily_stats,
            monthly_stats=[],  # Implementar similar a daily
            period_start=str(df['open_time'].min()),
            period_end=str(df['open_time'].max()),
            total_days=int((df['open_time'].max() - df['open_time'].min()).days),
            profit_distribution={},  # TODO: Histograma
            duration_distribution={}  # TODO: Histograma
        )
        
        return analytics
```

---

## 1.4 Endpoints API (FastAPI Routes)

### Endpoints para Análisis

```python
# app/api/v1/endpoints/analytics.py

from fastapi import APIRouter, File, UploadFile, Depends
from typing import List
import os
from app.services.trade_parser_service import TradeParserService
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import Analytics
from app.schemas.trade import Trade

router = APIRouter()

# UPLOAD
@router.post('/analytics/upload-trades')
async def upload_trades_file(file: UploadFile = File(...)):
    """
    Subir archivo CSV de operaciones MT5.
    
    Returns: {success, trades_count, file_path}
    """
    try:
        # Guardar archivo
        upload_dir = "data/raw"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = f"{upload_dir}/{file.filename}"
        with open(file_path, 'wb') as f:
            f.write(await file.read())
        
        # Parsear
        trades = TradeParserService.load_trades_from_csv(file_path)
        
        return {
            'success': True,
            'trades_count': len(trades),
            'file_path': file_path,
            'message': f'✅ {len(trades)} operaciones cargadas exitosamente'
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


# TRADES
@router.get('/analytics/trades', response_model=List[Trade])
async def get_trades():
    """
    Obtener lista de todas las operaciones.
    
    Parámetros opcionales:
    - symbol: Filtrar por par (EURUSD, GBPUSD)
    - status: GANADOR, PERDEDOR, BREAK_EVEN
    - limit: Últimas N operaciones
    - offset: Paginación
    """
    try:
        trades = TradeParserService.load_trades_from_csv('data/raw/operaciones_mt5.csv')
        return trades
    except Exception as e:
        return {'error': str(e)}


# ANALYTICS GENERAL
@router.get('/analytics/summary', response_model=Analytics)
async def get_analytics_summary():
    """
    Obtener resumen analítico completo con todos los KPIs.
    
    Incluye:
    - Estadísticas generales (win rate, profit factor, etc)
    - Curva de capital
    - Mejores/peores días
    - Estadísticas por símbolo
    - Series temporales
    """
    try:
        trades = TradeParserService.load_trades_from_csv('data/raw/operaciones_mt5.csv')
        TradeParserService.validate_trade_data(trades)
        analytics = AnalyticsService.calculate_all_analytics(trades)
        return analytics
    except Exception as e:
        return {'error': str(e)}


# FILTRADO AVANZADO
@router.get('/analytics/filter')
async def filter_trades(
    symbol: str = None,
    status: str = None,
    date_from: str = None,
    date_to: str = None,
    min_profit: float = None,
    max_profit: float = None
):
    """
    Filtrar operaciones por criterios múltiples.
    
    Ejemplo:
    GET /api/v1/analytics/filter?symbol=EURUSD&status=GANADOR&min_profit=100
    """
    try:
        trades = TradeParserService.load_trades_from_csv('data/raw/operaciones_mt5.csv')
        df = pd.DataFrame([t.dict() for t in trades])
        
        if symbol:
            df = df[df['symbol'] == symbol]
        if status:
            df = df[df['status'] == status]
        if date_from:
            df = df[df['open_time'] >= date_from]
        if date_to:
            df = df[df['open_time'] <= date_to]
        if min_profit is not None:
            df = df[df['profit_usd'] >= min_profit]
        if max_profit is not None:
            df = df[df['profit_usd'] <= max_profit]
        
        return {
            'filters_applied': {
                'symbol': symbol,
                'status': status,
                'date_from': date_from,
                'date_to': date_to,
                'min_profit': min_profit,
                'max_profit': max_profit
            },
            'results_count': len(df),
            'trades': df.to_dict('records')
        }
    except Exception as e:
        return {'error': str(e)}


# SERIE TEMPORAL (para gráficos)
@router.get('/analytics/timeseries')
async def get_timeseries(
    metric: str = 'equity',  # equity, daily_profit, cumulative_profit
    groupby: str = 'day'     # day, week, month
):
    """
    Obtener serie temporal para gráficos.
    
    Ejemplos:
    GET /api/v1/analytics/timeseries?metric=equity&groupby=day
    GET /api/v1/analytics/timeseries?metric=daily_profit&groupby=week
    """
    try:
        trades = TradeParserService.load_trades_from_csv('data/raw/operaciones_mt5.csv')
        analytics = AnalyticsService.calculate_all_analytics(trades)
        
        return {
            'metric': metric,
            'groupby': groupby,
            'dates': analytics.equity_dates,
            'values': analytics.equity_curve
        }
    except Exception as e:
        return {'error': str(e)}


# ESTADÍSTICAS POR SÍMBOLO
@router.get('/analytics/by-symbol')
async def get_symbol_stats():
    """
    Obtener estadísticas desglosadas por par (EURUSD, GBPUSD, etc).
    """
    try:
        trades = TradeParserService.load_trades_from_csv('data/raw/operaciones_mt5.csv')
        analytics = AnalyticsService.calculate_all_analytics(trades)
        
        return {
            'symbols': analytics.symbol_stats,
            'total_symbols': len(analytics.symbol_stats)
        }
    except Exception as e:
        return {'error': str(e)}


# HEATMAP HORARIO
@router.get('/analytics/hourly-heatmap')
async def get_hourly_heatmap():
    """
    Obtener rentabilidad por hora del día para heatmap.
    """
    try:
        trades = TradeParserService.load_trades_from_csv('data/raw/operaciones_mt5.csv')
        df = pd.DataFrame([t.dict() for t in trades])
        df['open_time'] = pd.to_datetime(df['open_time'])
        df['hour'] = df['open_time'].dt.hour
        
        hourly_stats = df.groupby('hour').agg({
            'profit_usd': ['sum', 'mean', 'count']
        }).round(2)
        
        return {
            'data': hourly_stats.to_dict(),
            'best_hour': df.groupby('hour')['profit_usd'].mean().idxmax()
        }
    except Exception as e:
        return {'error': str(e)}
```

---

## 1.5 Base de Datos (Modelo ORM - Futuro)

```python
# app/database/models.py (Para cuando escalemos con PostgreSQL)

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TradeORM(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    open_time = Column(DateTime, index=True)
    close_time = Column(DateTime)
    symbol = Column(String, index=True)
    order_type = Column(String)  # BUY/SELL
    volume = Column(Float)
    open_price = Column(Float)
    close_price = Column(Float)
    profit_usd = Column(Float)
    profit_pct = Column(Float)
    duration = Column(Integer)
    status = Column(String)  # GANADOR/PERDEDOR/BREAK_EVEN
    created_at = Column(DateTime, default=datetime.utcnow)
    
    class Config:
        orm_mode = True
```

---

## 1.6 requirements.txt Backend

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.0.0
pydantic-settings==2.0.0

# Data Processing
pandas==2.0.0
numpy==1.24.0
openpyxl==3.10.0  # Para leer Excel

# Analysis
scipy==1.11.0
scikit-learn==1.3.0  # Futuro: clustering de patterns

# Database (Futuro)
sqlalchemy==2.0.0
psycopg2-binary==2.9.0

# Utilities
python-dotenv==1.0.0
python-multipart==0.0.6
```

---

## 1.7 Estructura Final Backend

```
trading-bot-backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── api/v1/
│   │   └── endpoints/
│   │       ├── health.py
│   │       ├── analytics.py              🆕
│   │       └── trades.py                 🆕
│   ├── services/
│   │   ├── trade_parser_service.py       🆕
│   │   └── analytics_service.py          🆕
│   ├── schemas/
│   │   ├── trade.py                      🆕
│   │   └── analytics.py                  🆕
│   ├── database/
│   │   └── models.py                     🆕
│   └── utils/
│       └── cache.py                      (Para cachear KPIs)
├── data/
│   ├── raw/                              (Archivos CSV originales)
│   ├── processed/                        (Datos procesados)
│   └── cache/                            (KPIs cacheados)
├── tests/
│   └── test_analytics.py                 🆕
├── requirements.txt
└── .env
```

---

## 1.8 Endpoints Resumen

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/analytics/upload-trades` | Subir CSV de operaciones |
| GET | `/api/v1/analytics/trades` | Listar todas las operaciones |
| GET | `/api/v1/analytics/summary` | Resumen KPIs completo |
| GET | `/api/v1/analytics/filter` | Filtrar operaciones |
| GET | `/api/v1/analytics/timeseries` | Series temporales (para gráficos) |
| GET | `/api/v1/analytics/by-symbol` | Stats por par |
| GET | `/api/v1/analytics/hourly-heatmap` | Rentabilidad por hora |
| GET | `/api/v1/analytics/monthly-stats` | Stats por mes |
| GET | `/api/v1/analytics/daily-stats` | Stats diarios |

---

## 1.9 Flujo de Datos Backend

```
CSV Exportado (MT5)
        ↓
TradeParserService.load_trades_from_csv()
        ↓
List[Trade] (Datos validados)
        ↓
AnalyticsService.calculate_all_analytics()
        ↓
Analytics (KPIs calculados)
        ↓
Endpoint FastAPI
        ↓
JSON Response → Frontend
```

---

## 1.10 Notas Técnicas Backend

✅ **Implementación Inmediata:**
- CSV parser con pandas
- Cálculo de KPIs básicos
- 7 endpoints principales
- Pydantic schemas

⏳ **Fase 2 (Escalamiento):**
- PostgreSQL + SQLAlchemy ORM
- Caching con Redis
- Background jobs (Celery)
- WebSocket para updates real-time
- Validación OAuth con MT5 API

🔐 **Seguridad:**
- Validar integridad de datos
- Rate limiting en endpoints
- CORS configurado
- Input sanitization

📊 **Performance:**
- Cache KPIs (regenerar cada 24h o on-demand)
- Lazy loading de datos históricos
- Paginación en tablas grandes

