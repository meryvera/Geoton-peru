"""
GEOTÓN PERÚ 2026 — Índice de Vulnerabilidad Digital Compuesta (IVDC)
Dimensión 3: Capacidad Institucional Digital Municipal
Fuente: RENAMU 2025 — Formulario 01
Produce: 04-ok-renamu_distrital_limpio.csv

Variables clave:
  P14     → ¿tiene servicio de internet? (1=Sí, 2=No)
  P14A_1  → N° computadoras con acceso a internet
  P14A_2  → tipo de conexión (1=Wi-fi, 2=Móvil/USB, 3=ADSL, 4=Satelital, 5=Fibra óptica)
  P16_2   → usa SIAF (1=Sí, 0=No)
  P16_3   → usa SIGA (1=Sí, 0=No)
  Tipomuni → tipo de municipalidad (1=Provincial, 2=Distrital, 3=Centro Poblado)
"""

import pandas as pd
import numpy as np
import os

# ── Configuración ────────────────────────────────────────────────────────────
INPUT_FILE  = "Base-Datos_2025_f.csv"
OUTPUT_FILE = "04-ok-renamu_distrital_limpio.csv"

TIPO_CONEXION_LABELS = {
    1: "Wi-fi",
    2: "Móvil/USB",
    3: "ADSL/DSL",
    4: "Satelital",
    5: "Fibra óptica",
}
# Jerarquía de calidad de conexión (mayor número = más avanzado)
CONEXION_JERARQUIA = {5: 5, 3: 4, 1: 3, 2: 2, 4: 1}  # fibra>ADSL>wifi>móvil>satelital


# ── 1. Carga ─────────────────────────────────────────────────────────────────
print("=" * 65)
print("GEOTÓN PERÚ 2026 — Capacidad Institucional Digital Municipal")
print("=" * 65)

df = pd.read_csv(INPUT_FILE, sep=";", encoding="utf-8-sig", dtype=str)
df.columns = df.columns.str.strip()

print(f"\n[INFO] Registros totales cargados : {len(df):,}")
print(f"[INFO] Columnas en el archivo     : {len(df.columns)}")


# ── 2. Diagnóstico inicial ────────────────────────────────────────────────────
print("\n── Distribución de P14 (¿tiene internet?) ──────────────────────")
p14_raw = df["P14"].value_counts(dropna=False)
labels = {"1": "Sí tiene internet", "2": "No tiene internet"}
for val, cnt in p14_raw.items():
    lbl = labels.get(str(val), f"Valor '{val}'")
    pct = cnt / len(df) * 100
    print(f"  {lbl:25s}: {cnt:5d}  ({pct:.1f}%)")

print("\n── Distribución de P14A_2 (tipo de conexión) ───────────────────")
p14a2_raw = df["P14A_2"].value_counts(dropna=False)
for val, cnt in p14a2_raw.items():
    try:
        lbl = TIPO_CONEXION_LABELS.get(int(val), f"Valor '{val}'")
    except (ValueError, TypeError):
        lbl = f"Sin conexión / nulo ('{val}')"
    pct = cnt / len(df) * 100
    print(f"  {lbl:30s}: {cnt:5d}  ({pct:.1f}%)")

print("\n── Distribución de Tipomuni ─────────────────────────────────────")
tipo_lbl = {"1": "Provincial", "2": "Distrital", "3": "Centro Poblado"}
for val, cnt in df["Tipomuni"].value_counts(dropna=False).items():
    lbl = tipo_lbl.get(str(val), f"'{val}'")
    print(f"  {lbl:20s}: {cnt:5d}")


# ── 3. Limpieza y conversión de variables ────────────────────────────────────

def to_int_safe(series, valid_values=None):
    """Convierte a entero; valores inválidos o fuera de rango → NaN."""
    s = pd.to_numeric(series, errors="coerce")
    if valid_values is not None:
        s = s.where(s.isin(valid_values), other=np.nan)
    return s

df["_p14"]    = to_int_safe(df["P14"],    valid_values=[1, 2])
df["_p14a2"]  = to_int_safe(df["P14A_2"], valid_values=[1, 2, 3, 4, 5])
df["_p14a1"]  = to_int_safe(df["P14A_1"])          # N° computadoras con internet
df["_p16_2"]  = to_int_safe(df["P16_2"],  valid_values=[0, 1])
df["_p16_3"]  = to_int_safe(df["P16_3"],  valid_values=[0, 1])
df["_tipo"]   = to_int_safe(df["Tipomuni"])

# Ubigeo → siempre 6 dígitos con ceros
df["UBIGEO"] = df["Ubigeo"].astype(str).str.strip().str.zfill(6)


# ── 4. Filtrar y priorizar: Distrital > Provincial por UBIGEO ────────────────
df_dist  = df[df["_tipo"] == 2].copy()
df_prov  = df[df["_tipo"] == 1].copy()

ubigeos_con_distrital = set(df_dist["UBIGEO"])

# Para ubigeos sin registro distrital, incorporar el provincial
df_prov_sin_dist = df_prov[~df_prov["UBIGEO"].isin(ubigeos_con_distrital)].copy()
df_prov_sin_dist["_fuente"] = "provincial_fallback"
df_dist["_fuente"]          = "distrital"

df_work = pd.concat([df_dist, df_prov_sin_dist], ignore_index=True)

print(f"\n── Registros tras filtro Tipomuni ───────────────────────────────")
print(f"  Municipalidades distritales       : {len(df_dist):5d}")
print(f"  Ubigeos cubiertos por distritales : {df_dist['UBIGEO'].nunique():5d}")
print(f"  Provinciales incorporados como    ")
print(f"  fallback (sin distrital propio)   : {len(df_prov_sin_dist):5d}")
print(f"  Total registros a procesar        : {len(df_work):5d}")


# ── 5. Agregación por UBIGEO (puede haber duplicados por re-envíos) ───────────
def mejor_conexion(series):
    """Devuelve el tipo de conexión más avanzado del grupo."""
    vals = series.dropna()
    if vals.empty:
        return np.nan
    return vals.map(lambda x: CONEXION_JERARQUIA.get(int(x), 0)).idxmax() if False else \
           int(vals.map(lambda x: CONEXION_JERARQUIA.get(int(x), 0)).pipe(
               lambda s: vals.iloc[s.values.argmax()]))

def max_valido(s):
    s2 = s.dropna()
    return s2.max() if not s2.empty else np.nan

def first_valido(s):
    s2 = s.dropna()
    return s2.iloc[0] if not s2.empty else np.nan

agg = df_work.groupby("UBIGEO", as_index=False).agg(
    municipio_tiene_internet  = ("_p14",   lambda s: 1 if (s == 1).any() else 0),
    tipo_conexion_raw         = ("_p14a2", mejor_conexion),
    computadoras_con_internet = ("_p14a1", max_valido),
    usa_siaf                  = ("_p16_2", max_valido),
    usa_siga                  = ("_p16_3", max_valido),
    fuente                    = ("_fuente", first_valido),
)

# Mapear valores faltantes en SIAF/SIGA a 0 cuando sí hay internet
# (si no reportó, conservador: dejamos NaN como 0 para el score)
agg["usa_siaf"] = agg["usa_siaf"].fillna(0).astype(int)
agg["usa_siga"] = agg["usa_siga"].fillna(0).astype(int)

# tipo_conexion: etiqueta texto
agg["tipo_conexion"] = agg["tipo_conexion_raw"].apply(
    lambda x: TIPO_CONEXION_LABELS.get(int(x), "Desconocido") if pd.notna(x) else "Sin conexión"
)

# Índice de capacidad digital: suma de tres componentes (0–3)
agg["indice_capacidad_digital_municipal"] = (
    agg["municipio_tiene_internet"] +
    agg["usa_siaf"] +
    agg["usa_siga"]
)

# ── 6. Columnas finales en el orden pedido ────────────────────────────────────
output = agg[[
    "UBIGEO",
    "municipio_tiene_internet",
    "tipo_conexion",
    "computadoras_con_internet",
    "usa_siaf",
    "usa_siga",
    "indice_capacidad_digital_municipal",
    "fuente",
]].copy()

# computadoras_con_internet: entero o vacío
output["computadoras_con_internet"] = output["computadoras_con_internet"].apply(
    lambda x: int(x) if pd.notna(x) and x == x else ""
)


# ── 7. Diagnóstico de resultados ──────────────────────────────────────────────
total = len(output)
sin_internet = (output["municipio_tiene_internet"] == 0).sum()
con_internet = (output["municipio_tiene_internet"] == 1).sum()

print("\n── Resumen del dataset producido ────────────────────────────────")
print(f"  Ubigeos únicos en output          : {total:5d}")
print(f"  Municipios CON internet           : {con_internet:5d}  ({con_internet/total*100:.1f}%)")
print(f"  Municipios SIN internet           : {sin_internet:5d}  ({sin_internet/total*100:.1f}%)")

print("\n── Distribución del Índice (0–3) ────────────────────────────────")
for score, cnt in output["indice_capacidad_digital_municipal"].value_counts().sort_index().items():
    barra = "█" * int(cnt / total * 40)
    print(f"  Score {score}: {cnt:5d}  {barra}")

print("\n── Tipo de conexión (distribución final) ────────────────────────")
for conn, cnt in output["tipo_conexion"].value_counts().items():
    print(f"  {conn:25s}: {cnt:5d}  ({cnt/total*100:.1f}%)")

print("\n── Registros con fallback provincial ────────────────────────────")
fallback_n = (output["fuente"] == "provincial_fallback").sum()
print(f"  Ubigeos cubiertos por municipal   ")
print(f"  provincial (sin distrital propio) : {fallback_n:5d}")

print(f"\n── Distritos SIN internet — detalle ─────────────────────────────")
sin_df = output[output["municipio_tiene_internet"] == 0][["UBIGEO", "fuente"]].copy()
# Enriquecer con nombre de departamento (dos primeros dígitos de ubigeo)
ubigeo_info = df_work[["UBIGEO", "Departamento", "Provincia", "Distrito"]].drop_duplicates("UBIGEO")
sin_detalle = sin_df.merge(ubigeo_info, on="UBIGEO", how="left")
print(sin_detalle.to_string(index=False))


# ── 8. Guardar ────────────────────────────────────────────────────────────────
output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"\n[OK] Archivo guardado: {OUTPUT_FILE}  ({total} filas)")
print("=" * 65)
