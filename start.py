#!/usr/bin/env python3
"""
start.py — Levanta FastAPI + ngrok en un solo comando
======================================================
Uso:
    python start.py

Requisitos:
    pip install -r backend/requirements.txt
    pip install pyngrok

    # ngrok auth (solo la primera vez):
    ngrok config add-authtoken <TU_TOKEN>
"""

import subprocess
import time
import sys

try:
    from pyngrok import ngrok
except ImportError:
    print("Instala pyngrok:  pip install pyngrok")
    sys.exit(1)

PORT = 8000

def main():
    print(f"[start] Levantando FastAPI en localhost:{PORT} ...")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", str(PORT), "--reload"],
        cwd="backend",
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    time.sleep(2)

    print("[start] Abriendo túnel ngrok ...")
    tunnel = ngrok.connect(PORT, "http")
    public_url = tunnel.public_url

    print("\n" + "═" * 55)
    print(f"  URL PÚBLICA:  {public_url}")
    print(f"  App:          {public_url}/")
    print(f"  Docs API:     {public_url}/docs")
    print(f"  Health:       {public_url}/health")
    print("═" * 55)
    print("  Comparte la URL pública con quien quieras.")
    print("  Ctrl+C para detener todo.\n")

    try:
        server.wait()
    except KeyboardInterrupt:
        print("\n[start] Deteniendo...")
        ngrok.disconnect(public_url)
        server.terminate()

if __name__ == "__main__":
    main()
