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
            }
        }
