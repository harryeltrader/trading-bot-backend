# app/api/v1/endpoints/analytics.py

from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from typing import List, Optional
import os
import pandas as pd
from app.services.trade_parser_service import TradeParserService
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import Analytics
from app.schemas.trade import Trade

router = APIRouter()

# UPLOAD
@router.post('/upload-trades')
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
            content = await file.read()
            f.write(content)
        
        # Parsear
        trades = TradeParserService.load_trades_from_csv(file_path)
        
        return {
            'success': True,
            'trades_count': len(trades),
            'file_path': file_path,
            'message': f'✅ {len(trades)} operaciones cargadas exitosamente'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# TRADES
@router.get('/trades', response_model=List[Trade])
async def get_trades(
    limit: Optional[int] = Query(None, description="Límite de operaciones a retornar"),
    offset: Optional[int] = Query(0, description="Offset para paginación"),
    symbol: Optional[str] = Query(None, description="Filtrar por símbolo"),
    status: Optional[str] = Query(None, description="Filtrar por estado (GANADOR/PERDEDOR/BREAK_EVEN)")
):
    """
    Obtener lista de todas las operaciones.
    
    Parámetros opcionales:
    - symbol: Filtrar por par (EURUSD, GBPUSD)
    - status: GANADOR, PERDEDOR, BREAK_EVEN
    - limit: Últimas N operaciones
    - offset: Paginación
    """
    try:
        # Buscar archivo CSV en data/raw
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV. Por favor sube un archivo primero.")
        
        # Usar el archivo más reciente
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        
        # Filtrar
        if symbol:
            trades = [t for t in trades if t.symbol == symbol]
        if status:
            trades = [t for t in trades if t.status == status]
        
        # Paginación
        if limit:
            trades = trades[offset:offset+limit]
        
        return trades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ANALYTICS GENERAL
@router.get('/summary', response_model=Analytics)
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
        # Buscar archivo CSV en data/raw
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV. Por favor sube un archivo primero.")
        
        # Usar el archivo más reciente
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        TradeParserService.validate_trade_data(trades)
        analytics = AnalyticsService.calculate_all_analytics(trades)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# FILTRADO AVANZADO
@router.get('/filter')
async def filter_trades(
    symbol: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_profit: Optional[float] = None,
    max_profit: Optional[float] = None
):
    """
    Filtrar operaciones por criterios múltiples.
    
    Ejemplo:
    GET /api/v1/analytics/filter?symbol=EURUSD&status=GANADOR&min_profit=100
    """
    try:
        # Buscar archivo CSV en data/raw
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV")
        
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        df = pd.DataFrame([t.model_dump() for t in trades])
        
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
        raise HTTPException(status_code=500, detail=str(e))


# SERIE TEMPORAL (para gráficos)
@router.get('/timeseries')
async def get_timeseries(
    metric: str = Query('equity', description="Métrica a obtener (equity, daily_profit, cumulative_profit)"),
    groupby: str = Query('day', description="Agrupación (day, week, month)")
):
    """
    Obtener serie temporal para gráficos.
    
    Ejemplos:
    GET /api/v1/analytics/timeseries?metric=equity&groupby=day
    GET /api/v1/analytics/timeseries?metric=daily_profit&groupby=week
    """
    try:
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV")
        
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        analytics = AnalyticsService.calculate_all_analytics(trades)
        
        return {
            'metric': metric,
            'groupby': groupby,
            'dates': analytics.equity_dates,
            'values': analytics.equity_curve
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ESTADÍSTICAS POR SÍMBOLO
@router.get('/by-symbol')
async def get_symbol_stats():
    """
    Obtener estadísticas desglosadas por par (EURUSD, GBPUSD, etc).
    """
    try:
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV")
        
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        analytics = AnalyticsService.calculate_all_analytics(trades)
        
        return {
            'symbols': analytics.symbol_stats,
            'total_symbols': len(analytics.symbol_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# HEATMAP HORARIO
@router.get('/hourly-heatmap')
async def get_hourly_heatmap():
    """
    Obtener rentabilidad por hora del día para heatmap.
    """
    try:
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV")
        
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        df = pd.DataFrame([t.model_dump() for t in trades])
        df['open_time'] = pd.to_datetime(df['open_time'])
        df['hour'] = df['open_time'].dt.hour
        
        hourly_stats = df.groupby('hour').agg({
            'profit_usd': ['sum', 'mean', 'count']
        }).round(2)
        
        # Convertir a formato serializable
        result = {}
        for hour in range(24):
            if hour in hourly_stats.index:
                result[str(hour)] = {
                    'total': float(hourly_stats.loc[hour, ('profit_usd', 'sum')]),
                    'average': float(hourly_stats.loc[hour, ('profit_usd', 'mean')]),
                    'count': int(hourly_stats.loc[hour, ('profit_usd', 'count')])
                }
            else:
                result[str(hour)] = {'total': 0, 'average': 0, 'count': 0}
        
        best_hour = int(df.groupby('hour')['profit_usd'].mean().idxmax()) if len(df) > 0 else 0
        
        return {
            'data': result,
            'best_hour': best_hour
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ESTADÍSTICAS DIARIAS
@router.get('/daily-stats')
async def get_daily_stats():
    """
    Obtener estadísticas diarias.
    """
    try:
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV")
        
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        analytics = AnalyticsService.calculate_all_analytics(trades)
        
        return {
            'daily_stats': analytics.daily_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ESTADÍSTICAS MENSUALES
@router.get('/monthly-stats')
async def get_monthly_stats():
    """
    Obtener estadísticas mensuales.
    """
    try:
        raw_dir = "data/raw"
        csv_files = [f for f in os.listdir(raw_dir) if f.endswith('.csv')]
        
        if not csv_files:
            raise HTTPException(status_code=404, detail="No se encontraron archivos CSV")
        
        latest_file = max([os.path.join(raw_dir, f) for f in csv_files], key=os.path.getmtime)
        
        trades = TradeParserService.load_trades_from_csv(latest_file)
        analytics = AnalyticsService.calculate_all_analytics(trades)
        
        return {
            'monthly_stats': analytics.monthly_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
