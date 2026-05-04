import sys
import os
import pandas as pd
import pytest
from pathlib import Path

# Permitir importaciones locales
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_pipeline.limpieza import normalizar_cadena, simplificar_nombre, limpiar, COLUMNAS_MAP

def test_normalizar_cadena():
    assert normalizar_cadena("WALMART SUPERCENTER") == "Walmart"
    assert normalizar_cadena("soriana hiper") == "Soriana"
    assert normalizar_cadena("Bodega Aurrera Express") == "Walmart"
    assert normalizar_cadena("Oxxo") is None  # Cadena no permitida

def test_simplificar_nombre():
    assert simplificar_nombre("LECHE PASTEURIZADA LALA 1L") == "leche pasteurizada lala 1l"
    assert simplificar_nombre("  Pan   Bimbo  Blanco ") == "pan bimbo blanco"
    assert simplificar_nombre("Huevo San Juan (18 pzas)") == "huevo san juan 18 pzas"

def test_pipeline_limpiar():
    # Simulamos un dataframe crudo cargado desde CSV
    data = {
        "cadena_comercial": ["WALMART", "OXXO", "SORIANA", "CHEDRAUI"],
        "producto": ["Leche", "Papas", "Huevo", "Pan"],
        "precio": ["25.5", "15.0", "-10", "abc"], # Un negativo y un inválido
        "latitud": ["19.4", "19.5", "19.6", "19.7"],
        "longitud": ["-99.1", "-99.2", "-99.3", ""] # Coordenada faltante
    }
    df = pd.DataFrame(data)
    # Renombramos a formato interno como lo hace cargar_csv
    df = df.rename(columns=COLUMNAS_MAP)
    
    df_limpio = limpiar(df)
    
    # 1. OXXO debe ser descartado (cadena no permitida)
    assert "Oxxo" not in df_limpio["cadena"].values
    
    # 2. El huevo (-10) debe ser descartado
    assert not any(df_limpio["producto"] == "huevo")
    
    # 3. El pan con precio inválido y coordenada faltante debe ser descartado
    assert not any(df_limpio["producto"] == "pan")
    
    # 4. Solo la leche de Walmart debería sobrevivir
    assert len(df_limpio) == 1
    assert df_limpio.iloc[0]["producto"] == "leche"
    assert df_limpio.iloc[0]["precio"] == 25.5
