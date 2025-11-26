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
        
        df = pd.DataFrame([t.model_dump() for t in trades])
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
        
        win_streaks = streaks[df.groupby('streak_group')['profit_usd'].sum() > 0]
        loss_streaks = streaks[df.groupby('streak_group')['profit_usd'].sum() < 0]
        
        longest_win = int(win_streaks.max()) if len(win_streaks) > 0 else 0
        longest_loss = int(loss_streaks.max()) if len(loss_streaks) > 0 else 0
        
        # MEJOR/PEOR DÍA
        daily = df.groupby(df['open_time'].dt.date)['profit_usd'].sum()
        best_day = str(daily.idxmax()) if len(daily) > 0 else ""
        best_day_profit = float(daily.max()) if len(daily) > 0 else 0.0
        worst_day = str(daily.idxmin()) if len(daily) > 0 else ""
        worst_day_profit = float(daily.min()) if len(daily) > 0 else 0.0
        
        # MEJOR HORA
        df['hour'] = df['open_time'].dt.hour
        hourly = df.groupby('hour')['profit_usd'].mean()
        best_hour = int(hourly.idxmax()) if len(hourly) > 0 else 0
        best_hour_profit = float(hourly.max()) if len(hourly) > 0 else 0.0
        
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
        
        # ESTADÍSTICAS MENSUALES
        monthly_stats = []
        df['month'] = df['open_time'].dt.to_period('M')
        for month, group in df.groupby('month'):
            group_by_date = group.groupby(group['open_time'].dt.date)['profit_usd'].sum()
            monthly_stats.append(MonthlyStats(
                month=str(month),
                trades=len(group),
                profit=float(group['profit_usd'].sum()),
                win_rate=float((len(group[group['profit_usd'] > 0]) / len(group) * 100) if len(group) > 0 else 0),
                best_day=str(group_by_date.idxmax()) if len(group_by_date) > 0 else "",
                worst_day=str(group_by_date.idxmin()) if len(group_by_date) > 0 else ""
            ))
        
        # DISTRIBUCIÓN DE GANANCIAS
        profit_bins = [-float('inf'), -1000, -500, -100, 0, 100, 500, 1000, float('inf')]
        profit_distribution = df['profit_usd'].value_counts(bins=profit_bins, sort=False).to_dict()
        profit_distribution = {str(k): int(v) for k, v in profit_distribution.items()}
        
        # DISTRIBUCIÓN DE DURACIONES
        duration_bins = [0, 30, 60, 120, 240, 480, 1440, float('inf')]
        duration_distribution = df['duration'].value_counts(bins=duration_bins, sort=False).to_dict()
        duration_distribution = {str(k): int(v) for k, v in duration_distribution.items()}
        
        # CONSTRUIR OBJETO ANALYTICS
        analytics = Analytics(
            total_trades=total_trades,
            winning_trades=winning,
            losing_trades=losing,
            break_even=break_even,
            total_profit=float(total_profit),
            total_profit_pct=float((total_profit / abs(df['open_price'].iloc[0] * df['volume'].iloc[0] * 100000)) * 100) if len(df) > 0 else 0,
            average_profit=float(df['profit_usd'].mean()),
            win_rate=float(win_rate),
            profit_factor=float(profit_factor),
            payoff_ratio=float(payoff_ratio),
            max_drawdown=float(max_drawdown),
            max_drawdown_pct=float(max_drawdown_pct),
            current_drawdown=float(drawdown.iloc[-1]) if len(drawdown) > 0 else 0,
            longest_win_streak=longest_win,
            longest_loss_streak=longest_loss,
            current_streak=int(df['sign'].iloc[-1] if len(df) > 0 else 0),
            symbol_stats=symbol_stats,
            best_day=best_day,
            best_day_profit=best_day_profit,
            worst_day=worst_day,
            worst_day_profit=worst_day_profit,
            best_hour=best_hour,
            best_hour_profit=best_hour_profit,
            equity_curve=equity_curve,
            equity_dates=equity_dates,
            daily_stats=daily_stats,
            monthly_stats=monthly_stats,
            period_start=str(df['open_time'].min()) if len(df) > 0 else "",
            period_end=str(df['open_time'].max()) if len(df) > 0 else "",
            total_days=int((df['open_time'].max() - df['open_time'].min()).days) if len(df) > 0 else 0,
            profit_distribution=profit_distribution,
            duration_distribution=duration_distribution
        )
        
        return analytics
