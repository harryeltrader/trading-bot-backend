# tests/test_analytics.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert "Trading Portfolio Analytics API" in response.json()["service"]


def test_health_check():
    """Test del health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_summary_without_data():
    """Test del endpoint de summary sin datos cargados"""
    response = client.get("/api/v1/analytics/summary")
    # Debería retornar 404 si no hay archivos CSV
    assert response.status_code in [404, 500]


def test_get_trades_without_data():
    """Test del endpoint de trades sin datos cargados"""
    response = client.get("/api/v1/analytics/trades")
    # Debería retornar 404 si no hay archivos CSV
    assert response.status_code in [404, 500]


def test_get_symbol_stats_without_data():
    """Test del endpoint de symbol stats sin datos cargados"""
    response = client.get("/api/v1/analytics/by-symbol")
    # Debería retornar 404 si no hay archivos CSV
    assert response.status_code in [404, 500]


# TODO: Agregar tests con datos de prueba
# - Test de upload de CSV
# - Test de cálculo de KPIs
# - Test de filtrado
# - Test de series temporales
