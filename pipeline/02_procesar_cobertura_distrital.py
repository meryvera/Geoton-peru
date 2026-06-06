"""
procesar_cobertura_distrital.py
Geotón Perú 2026 — Índice de Vulnerabilidad Digital Compuesta (IVDC)

Lee cobertura_movil_ccpp_atributos.csv y genera 02-ok-cobertura_movil_distrital_limpio.csv
con indicadores de cobertura móvil agregados a nivel distrital.

UBIGEO: se construye cruzando NOM_DPTO + NOM_PROV + NOM_DIST contra la tabla
oficial Lista_Ubigeos_INEI.csv (separada por punto y coma).
Los COD_DPTO/COD_PROV/COD_DIST del shapefile original están vacíos (bug de origen).

Archivos requeridos en el mismo directorio:
  - cobertura_movil_ccpp_atributos.csv
  - Lista_Ubigeos_INEI.csv

Uso:
    python procesar_cobertura_distrital.py
    python procesar_cobertura_distrital.py input.csv output.csv ubigeo.csv
"""

import sys
import unicodedata
import pandas as pd

INPUT_CSV  = sys.argv[1] if len(sys.argv) > 1 else "cobertura_movil_ccpp_atributos.csv"
OUTPUT_CSV = sys.argv[2] if len(sys.argv) > 2 else "02-ok-cobertura_movil_distrital_limpio.csv"
UBIGEO_CSV = sys.argv[3] if len(sys.argv) > 3 else "Lista_Ubigeos_INEI.csv"

OPERADORES = {
    "COB_BIT":   "BITEL",
    "COB_CLARO": "CLARO",
    "COB_ENTEL": "ENTEL",
    "COB_MOVIS": "MOVISTAR",
}

# Correcciones de nombres: OSIPTEL usa nombres distintos al INEI en 19 distritos.
# Formato: (NOM_DPTO, NOM_PROV, NOM_DIST) en OSIPTEL → (DEPARTAMENTO, PROVINCIA, DISTRITO) en INEI
CORRECCIONES = {
    ("AMAZONAS",      "LUYA",           "SAN FRANCISCO DEL YESO"):    ("AMAZONAS",      "LUYA",      "SAN FRANCISCO DE YESO"),
    ("APURIMAC",      "AYMARAES",       "IHUAYLLO"):                   ("APURIMAC",      "AYMARAES",  "HUAYLLU"),
    ("APURIMAC",      "GRAU",           "GAMARRA"):                    ("APURIMAC",      "GRAU",      "MARISCAL GAMARRA"),
    ("CAJAMARCA",     "CONTUMAZA",      "SANTA CRUZ DE TOLED"):        ("CAJAMARCA",     "CONTUMAZA", "SANTA CRUZ DE TOLEDO"),
    ("CALLAO",        "CALLAO",         "CARMEN DE LA LEGUA REYNOSO"): ("CALLAO",        "CALLAO",    "CARMEN DE LA LEGUA-REYNOSO"),
    ("HUANCAVELICA",  "HUAYTARA",       "QUITO-ARMA"):                 ("HUANCAVELICA",  "HUAYTARA",  "QUITO ARMA"),
    ("HUANUCO",       "HUANUCO",        "QUISQUI (KICHKI)"):           ("HUANUCO",       "HUANUCO",   "QUISQUI"),
    ("ICA",           "NASCA",          "NASCA"):                      ("ICA",           "NAZCA",     "NASCA"),
    ("ICA",           "NASCA",          "CHANGUILLO"):                 ("ICA",           "NAZCA",     "CHANGUILLO"),
    ("ICA",           "NASCA",          "EL INGENIO"):                 ("ICA",           "NAZCA",     "EL INGENIO"),
    ("ICA",           "NASCA",          "MARCONA"):                    ("ICA",           "NAZCA",     "MARCONA"),
    ("ICA",           "NASCA",          "VISTA ALEGRE"):               ("ICA",           "NAZCA",     "VISTA ALEGRE"),
    ("JUNIN",         "CHUPACA",        "SAN JUAN DE ISCOS"):          ("JUNIN",         "CHUPACA",   "SAN JUAN DE YSCOS"),
    ("LIMA",          "HUAROCHIRI",     "SAN PEDRO DE LARAOS"):        ("LIMA",          "HUAROCHIRI","SAN PEDRO LARAOS"),
    ("PIURA",         "SECHURA",        "RINCONADA LLICUAR"):          ("PIURA",         "SECHURA",   "RINCONADA-LLICUAR"),
    ("SAN MARTIN",    "PICOTA",         "CASPISAPA"):                  ("SAN MARTIN",    "PICOTA",    "CASPIZAPA"),
    ("TACNA",         "TARATA",         "ESTIQUE-PAMPA"):              ("TACNA",         "TARATA",    "ESTIQUE PAMPA"),
    # HUALLA (VICTOR FAJARDO) y ALLAUCA (YAUYOS) no existen en el INEI → quedan sin ubigeo
}


def norm(t):
    """Mayúsculas, sin tildes, sin espacios extra."""
    if pd.isna(t):
        return ""
    s = str(t).strip().upper()
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


# ── 1. Leer dataset ────────────────────────────────────────────────────────────
print(f"[1/6] Leyendo {INPUT_CSV} ...")
df = pd.read_csv(INPUT_CSV, dtype=str, encoding="utf-8-sig")
print(f"      Registros  : {len(df):,}")
print(f"      Columnas   : {len(df.columns)}")
print(f"      COB_TOTAL  → SI: {(df['COB_TOTAL']=='SI').sum():,}  NO: {(df['COB_TOTAL']=='NO').sum():,}")
print(f"      CLASIFIC   → {df['CLASIFIC'].value_counts().to_dict()}")


# ── 2. Eliminar duplicados ─────────────────────────────────────────────────────
print("[2/6] Eliminando duplicados (NOMBCCPP + LONG_X + LAT_Y) ...")
antes = len(df)
df = df.drop_duplicates(subset=["NOMBCCPP", "LONG_X", "LAT_Y"], keep="first")
print(f"      Eliminados : {antes - len(df)}  |  Restantes: {len(df):,}")


# ── 3. Construir lookup ubigeo desde tabla INEI ────────────────────────────────
print(f"[3/6] Cargando {UBIGEO_CSV} ...")
ub = pd.read_csv(UBIGEO_CSV, dtype=str, encoding="utf-8-sig", sep=";")
ub["_d"]  = ub["DEPARTAMENTO"].apply(norm)
ub["_p"]  = ub["PROVINCIA"].apply(norm)
ub["_di"] = ub["DISTRITO"].apply(norm)
lookup = {
    (r["_d"], r["_p"], r["_di"]): r["UBIGEO_INEI"].strip().zfill(6)
    for _, r in ub.iterrows()
}
print(f"      Lookup INEI: {len(lookup):,} distritos")


# ── 4. Aplicar correcciones de nombres y asignar UBIGEO ───────────────────────
print("[4/6] Asignando UBIGEO ...")

def get_ubigeo(row):
    key_orig = (row["NOM_DPTO"].strip().upper(),
                row["NOM_PROV"].strip().upper(),
                row["NOM_DIST"].strip().upper())
    # Aplicar corrección si existe
    key_corr = CORRECCIONES.get(key_orig, key_orig)
    # Normalizar y buscar en lookup
    key_norm = tuple(norm(x) for x in key_corr)
    return lookup.get(key_norm)

df["UBIGEO"] = df.apply(get_ubigeo, axis=1)

con_ubigeo = df["UBIGEO"].notna().sum()
sin_ubigeo = df["UBIGEO"].isna().sum()
print(f"      Con UBIGEO : {con_ubigeo:,} ({con_ubigeo/len(df)*100:.2f}%)")
print(f"      Sin UBIGEO : {sin_ubigeo:,} ({sin_ubigeo/len(df)*100:.2f}%)")

if sin_ubigeo > 0:
    distritos_sin = (
        df[df["UBIGEO"].isna()][["NOM_DPTO","NOM_PROV","NOM_DIST"]]
        .drop_duplicates()
    )
    print(f"      Distritos sin match ({len(distritos_sin)}):")
    for _, r in distritos_sin.iterrows():
        print(f"        {r['NOM_DPTO']} / {r['NOM_PROV']} / {r['NOM_DIST']}")
    print("      (Estos distritos no existen en la tabla INEI descargada)")


# ── 5. Flags por centro poblado ────────────────────────────────────────────────
print("[5/6] Calculando indicadores por centro poblado ...")
df["es_rural"]      = df["CLASIFIC"].str.strip().str.upper() == "RURAL"
df["sin_cobertura"] = df["COB_TOTAL"].str.strip().str.upper() == "NO"
df["n_operadores"]  = sum(
    (df[col].str.strip().str.upper() == "SI").astype(int) for col in OPERADORES
)
df["cob_parcial"] = (df["n_operadores"] > 0) & (df["n_operadores"] < 4)


# ── 6. Agregar a nivel distrital ───────────────────────────────────────────────
print("[6/6] Agregando a nivel distrital ...")

# Solo registros con UBIGEO válido
df_valido = df[df["UBIGEO"].notna()].copy()

def agg_distrito(g):
    total       = len(g)
    sin_cob     = int(g["sin_cobertura"].sum())
    rurales     = int(g["es_rural"].sum())
    rurales_sin = int((g["es_rural"] & g["sin_cobertura"]).sum())
    parcial     = int(g["cob_parcial"].sum())
    op_counts   = {
        label: int((g[col].str.strip().str.upper() == "SI").sum())
        for col, label in OPERADORES.items()
    }
    op_dom = "NINGUNO" if max(op_counts.values()) == 0 else max(op_counts, key=op_counts.get)
    return pd.Series({
        "total_ccpp":                 total,
        "ccpp_sin_cobertura":         sin_cob,
        "pct_sin_cobertura":          round(sin_cob / total * 100, 2) if total else None,
        "ccpp_rurales_sin_cobertura": rurales_sin,
        "pct_rurales_sin_cobertura":  round(rurales_sin / rurales * 100, 2) if rurales else None,
        "ccpp_con_cobertura_parcial": parcial,
        "operador_dominante":         op_dom,
    })

resultado = df_valido.groupby("UBIGEO").apply(agg_distrito).reset_index()
resultado = resultado[[
    "UBIGEO", "total_ccpp", "ccpp_sin_cobertura", "pct_sin_cobertura",
    "ccpp_rurales_sin_cobertura", "pct_rurales_sin_cobertura",
    "ccpp_con_cobertura_parcial", "operador_dominante",
]]

resultado.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

# ── Resumen final ──────────────────────────────────────────────────────────────
print()
print("=" * 65)
print(f"  Archivo generado             : {OUTPUT_CSV}")
print(f"  Distritos en output          : {len(resultado):,}")
print(f"  CC.PP. procesados            : {len(df_valido):,} / {len(df):,}")
print(f"  Distritos 100% sin cobertura : {(resultado['pct_sin_cobertura']==100.0).sum():,}")
print(f"  Distritos cobertura total    : {(resultado['pct_sin_cobertura']==0.0).sum():,}")
print(f"  Operador dominante nacional  : {resultado['operador_dominante'].value_counts().idxmax()}")
print(f"  UBIGEO fuente                : {UBIGEO_CSV} (INEI oficial)")
if sin_ubigeo > 0:
    print(f"  ⚠  {sin_ubigeo} CC.PP. sin UBIGEO (HUALLA y ALLAUCA — no existen en INEI)")
print("=" * 65)
