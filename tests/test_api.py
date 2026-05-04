import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Asegurar que importamos desde backend/ correctamente
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from main import app

client = TestClient(app)

def test_health_check():
    """Prueba que el servidor encienda y el endpoint de salud responda 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "mongodb_connected" in data

def test_frontend_serve():
    """Prueba que el Frontend estático se está sirviendo correctamente."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_optimizar_carrito_payload_invalido():
    """Prueba la validación de Pydantic al enviar un payload incorrecto."""
    response = client.post("/api/v1/optimizar-carrito", json={"ubicacion_usuario": {"latitud": "letras"}})
    assert response.status_code == 422 # Unprocessable Entity (Validación fallida)
