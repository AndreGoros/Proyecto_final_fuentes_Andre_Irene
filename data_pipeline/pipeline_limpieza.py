"""
pipeline_limpieza.py
====================
Entry point del pipeline de limpieza de datos de precios por cadena comercial.

Uso (desde la raíz del proyecto):
    python data_pipeline/pipeline_limpieza.py
    python data_pipeline/pipeline_limpieza.py archivo1.csv archivo2.csv
    python data_pipeline/pipeline_limpieza.py --no-mongo

La lógica vive en `data_pipeline/limpieza.py`.
"""
import sys
from pathlib import Path

# Permite importar limpieza.py sin importar desde dónde se ejecute el script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from limpieza import main_cli

if __name__ == "__main__":
    main_cli()
