"""
build_pronatel_distrital.py
----------------------------
Agrega localidades beneficiarias PRONATEL a nivel distrital.
Produce: 03-ok-pronatel_localidades_distrital_limpio.csv

Valores únicos de ESTADO_PY detectados:
  [EN OPERACION]           → operativo
  [EN IMPLEMENTACION]      → en_ejecucion
  [REFORMULACION-REGIONAL] → proyectada
  texto largo (3 filas)    → en_ejecucion (proceso activo, no planificado)
"""

import pandas as pd
import os

import os

# Ajusta estas rutas si el script y el CSV están en carpetas distintas
INPUT_FILE  = os.getenv("INPUT_FILE",  "localidades_beneficiarias_atributos.csv")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "03-ok-pronatel_localidades_distrital_limpio.csv")

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(
    INPUT_FILE,
    dtype={"cod_dist": str, "cod_dpto": str, "cod_prov": str, "cod_ccpp": str},
)

# ── 2. Verificar UBIGEO ───────────────────────────────────────────────────────
assert (df["cod_dist"].str.len() == 6).all(), "ERROR: cod_dist con longitud != 6"
print(f"✔ Registros leídos : {len(df):,}")
print(f"✔ Distritos únicos : {df['cod_dist'].nunique():,}")

# ── 3. Clasificar ESTADO_PY ───────────────────────────────────────────────────
def clasificar_estado(val):
    v = str(val).strip().upper()
    if v == "[EN OPERACION]":
        return "operativo"
    elif v == "[REFORMULACION-REGIONAL]":
        return "proyectada"
    else:
        # [EN IMPLEMENTACION] y el texto largo de 3 filas
        return "en_ejecucion"

df["estado_cat"] = df["ESTADO_PY"].apply(clasificar_estado)

print("\nClasificación de ESTADO_PY:")
print(df.groupby("ESTADO_PY")["estado_cat"].first().to_string())

# ── 4. POB_2023 = 0 → NaN solo para sumas de población ───────────────────────
df["pob_para_suma"] = df["POB_2023"].where(df["POB_2023"] > 0, other=pd.NA)

# ── 5. Flags por categoría ────────────────────────────────────────────────────
df["es_operativo"]     = df["estado_cat"] == "operativo"
df["es_en_ejecucion"]  = df["estado_cat"] == "en_ejecucion"
df["es_proyectada"]    = df["estado_cat"] == "proyectada"

# ── 6. Agregación distrital ───────────────────────────────────────────────────
agg = df.groupby("cod_dist").agg(
    total_localidades_pronatel = ("cod_dist", "count"),
    localidades_operativas     = ("es_operativo",    "sum"),
    localidades_en_ejecucion   = ("es_en_ejecucion", "sum"),
    localidades_proyectadas    = ("es_proyectada",   "sum"),
    pob_cubierta_operativo     = ("pob_para_suma",
                                   lambda s: df.loc[
                                       s.index[df.loc[s.index, "es_operativo"]], "pob_para_suma"
                                   ].sum(min_count=1)),
    iiee_cubiertos             = ("IIEE_PY",
                                   lambda s: df.loc[
                                       s.index[df.loc[s.index, "es_operativo"]], "IIEE_PY"
                                   ].sum()),
    eess_cubiertos             = ("EESS_PY",
                                   lambda s: df.loc[
                                       s.index[df.loc[s.index, "es_operativo"]], "EESS_PY"
                                   ].sum()),
    dp_cubiertos               = ("DP_PY",
                                   lambda s: df.loc[
                                       s.index[df.loc[s.index, "es_operativo"]], "DP_PY"
                                   ].sum()),
).reset_index()

# ── 7. Porcentaje operativo ───────────────────────────────────────────────────
agg["pct_operativo"] = (
    agg["localidades_operativas"] / agg["total_localidades_pronatel"] * 100
).round(2)

# ── 8. Renombrar UBIGEO ───────────────────────────────────────────────────────
agg.rename(columns={"cod_dist": "UBIGEO"}, inplace=True)

# ── 9. Convertir tipos enteros ────────────────────────────────────────────────
int_cols = [
    "total_localidades_pronatel", "localidades_operativas",
    "localidades_en_ejecucion", "localidades_proyectadas",
    "iiee_cubiertos", "eess_cubiertos", "dp_cubiertos",
]
agg[int_cols] = agg[int_cols].astype(int)

# pob_cubierta_operativo puede tener NaN si todos los operativos tienen POB=0
agg["pob_cubierta_operativo"] = agg["pob_cubierta_operativo"].fillna(0).astype(int)

# ── 10. Orden de columnas ─────────────────────────────────────────────────────
cols = [
    "UBIGEO",
    "total_localidades_pronatel",
    "localidades_operativas",
    "localidades_en_ejecucion",
    "localidades_proyectadas",
    "pct_operativo",
    "pob_cubierta_operativo",
    "iiee_cubiertos",
    "eess_cubiertos",
    "dp_cubiertos",
]
agg = agg[cols].sort_values("UBIGEO").reset_index(drop=True)

# ── 11. Guardar ───────────────────────────────────────────────────────────────
agg.to_csv(OUTPUT_FILE, index=False)

print(f"\n✔ Distritos en output         : {len(agg):,}")
print(f"✔ Archivo guardado            : {OUTPUT_FILE}")
print(f"\nResumen:")
print(f"  Total localidades procesadas : {agg['total_localidades_pronatel'].sum():,}")
print(f"  Localidades operativas       : {agg['localidades_operativas'].sum():,}")
print(f"  Localidades en ejecución     : {agg['localidades_en_ejecucion'].sum():,}")
print(f"  Localidades proyectadas      : {agg['localidades_proyectadas'].sum():,}")
print(f"  Población cubierta (operativo): {agg['pob_cubierta_operativo'].sum():,}")
print(f"\nPrimeras 5 filas:")
print(agg.head().to_string(index=False))
