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
    spread: Optional[float] = None   # Spread en pips
    comment: Optional[str] = None    # Comentario/nota
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
