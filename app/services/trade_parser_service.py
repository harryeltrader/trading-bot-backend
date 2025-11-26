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
                'Comente': 'comment',
                # English column names (fallback)
                'Open Time': 'open_time',
                'Close Time': 'close_time',
                'Symbol': 'symbol',
                'Type': 'order_type',
                'Volume': 'volume',
                'Open Price': 'open_price',
                'Close Price': 'close_price',
                'Profit': 'profit_usd',
                'Comment': 'comment'
            }
            df.rename(columns=column_mapping, inplace=True)
            
            trades = []
            for idx, row in df.iterrows():
                # Calcular profit_pct de forma segura
                try:
                    profit_pct = (float(row['profit_usd']) / abs(float(row['open_price']) * float(row['volume']) * 100)) * 100
                except (ZeroDivisionError, ValueError):
                    profit_pct = 0.0
                
                # Calcular duración
                try:
                    open_dt = pd.to_datetime(row['open_time'])
                    close_dt = pd.to_datetime(row['close_time'])
                    duration = int((close_dt - open_dt).total_seconds() / 60)
                except:
                    duration = 0
                
                trade = Trade(
                    id=int(idx),
                    open_time=pd.to_datetime(row['open_time']),
                    close_time=pd.to_datetime(row['close_time']),
                    symbol=str(row['symbol']).strip(),
                    order_type=str(row['order_type']).upper(),
                    volume=float(row['volume']),
                    open_price=float(row['open_price']),
                    close_price=float(row['close_price']),
                    profit_usd=float(row['profit_usd']),
                    profit_pct=profit_pct,
                    duration=duration,
                    spread=float(row.get('spread', 0)) if 'spread' in row else None,
                    comment=str(row.get('comment', '')) if 'comment' in row else None,
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
