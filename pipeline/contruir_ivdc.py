"""
IVDC v2 — Índice de Vulnerabilidad Digital Compuesta
Estructura sectorial: 1 índice base + 4 índices sectoriales
Geotón Perú 2026
================================================================

NUEVA ARQUITECTURA:
  BASE   — Cobertura de señal móvil (OSIPTEL) → prerequisito
  S1     — Conectividad educativa (PRONATEL/escuelas)
  S2     — Conectividad en salud (PRONATEL/establecimientos)
  S3     — Capacidad digital municipal (RENAMU)
  S4     — Presencia policial conectada (PRONATEL/PNP)

  IVDC = promedio(S1..S4) * (1 + penalidad_base)
  donde penalidad_base amplifica vulnerabilidad si no hay señal

VALIDACIÓN:
  - IVDC vs IDH (Pearson + Spearman)
  - S1 vs años de educación (componente IDH)
  - S2 vs esperanza de vida (componente IDH)
  - S3 vs ingreso per cápita (componente IDH)
  - S4 vs IDH general (proxy de presencia estatal)

OUTPUTS:
  1. ivdc_v2_distrital_final.csv
  2. ivdc_v2_tabla_departamental.csv
  3. ivdc_v2_reporte_metodologico.txt
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import MinMaxScaler
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = "/content/"
OUT_DIR  = "/content/"

# ================================================================
# 0. CARGA
# ================================================================
print("=" * 65)
print("PASO 0 — Carga de archivos")
print("=" * 65)

idh = pd.read_csv(DATA_DIR + "01-ok-idh_distrital_limpio.csv",
                  dtype={"UBIGEO": str})
mov = pd.read_csv(DATA_DIR + "02-ok-cobertura_movil_distrital_limpio.csv",
                  dtype={"UBIGEO": str})
dep = pd.read_csv(DATA_DIR + "03-ok-dependencias_policiales_distrital_limpio.csv",
                  dtype={"UBIGEO": str})
esc = pd.read_csv(DATA_DIR + "03-ok-escuelas_distrital_limpio.csv",
                  dtype={"UBIGEO": str})
sal = pd.read_csv(DATA_DIR + "03-ok-salud_distrital_limpio.csv",
                  dtype={"UBIGEO": str})
ren = pd.read_csv(DATA_DIR + "04-ok-renamu_distrital_limpio.csv",
                  dtype={"UBIGEO": str})

for name, df_ in [("IDH",idh),("Cobertura",mov),("Policiales",dep),
                  ("Escuelas",esc),("Salud",sal),("RENAMU",ren)]:
    print(f"  {name:12s}: {len(df_):>5} filas")

# ================================================================
# 1. CORRECCIONES
# ================================================================
print("\n" + "=" * 65)
print("PASO 1 — Correcciones de datos")
print("=" * 65)

def strip_pct(s):
    return pd.to_numeric(s.astype(str).str.replace('%','',regex=False),
                         errors='coerce')

esc['pct_escuelas_operativas']         = strip_pct(esc['pct_escuelas_operativas'])
sal['pct_establecimientos_operativos'] = strip_pct(sal['pct_establecimientos_operativos'])
mov['pct_sin_cobertura']               = pd.to_numeric(mov['pct_sin_cobertura'],
                                                        errors='coerce')

# RENAMU: índice ordinal calidad conexión 0-5
orden = {'Sin conexión':0,'Móvil/USB':1,'Satelital':2,
         'Wi-fi':3,'ADSL/DSL':4,'Fibra óptica':5}
ren['calidad_conexion'] = ren['tipo_conexion'].map(orden).fillna(0).astype(int)

# Imputar 3 distritos sin cobertura móvil (promedio departamental)
mov['dpto'] = mov['UBIGEO'].str[:2]
prom_dpto   = mov.groupby('dpto')['pct_sin_cobertura'].mean()
faltantes   = set(idh['UBIGEO']) - set(mov['UBIGEO'])
parches = []
for ub in faltantes:
    valor = prom_dpto.get(ub[:2], mov['pct_sin_cobertura'].mean())
    parches.append({'UBIGEO': ub, 'pct_sin_cobertura': round(valor,2)})
    print(f"  Imputado {ub}: {valor:.2f}% (promedio depto {ub[:2]})")
if parches:
    mov = pd.concat([mov, pd.DataFrame(parches)], ignore_index=True)

print(f"  [OK] Escuelas y salud: % convertidos a numérico")
print(f"  [OK] RENAMU: calidad_conexion ordinal 0-5")
print(f"  [OK] Cobertura móvil: {len(faltantes)} imputados")

# ================================================================
# 2. BASE: 1,874 DISTRITOS DEL IDH
# ================================================================
print("\n" + "=" * 65)
print("PASO 2 — Construcción base distrital")
print("=" * 65)

base = idh[['UBIGEO','NOM_DPTO','NOM_PROV','NOM_DIST',
            'IDH','quintil_idh','ingreso_per_capita',
            'esperanza_vida','anios_educacion']].copy()
base['IDH_num'] = pd.to_numeric(base['IDH'], errors='coerce')

# ── ÍNDICE BASE: cobertura de señal ──────────────────────────────
mov_c = mov[['UBIGEO','pct_sin_cobertura']].drop_duplicates('UBIGEO')
base  = base.merge(mov_c, on='UBIGEO', how='left')
base['pct_sin_cobertura'] = base['pct_sin_cobertura'].fillna(
    mov['pct_sin_cobertura'].mean())
print(f"  BASE (señal): media={base['pct_sin_cobertura'].mean():.1f}%  "
      f"max={base['pct_sin_cobertura'].max():.1f}%")

# ── S1: Conectividad educativa ────────────────────────────────────
esc_c = esc[['UBIGEO','pct_escuelas_operativas']].drop_duplicates('UBIGEO')
base  = base.merge(esc_c, on='UBIGEO', how='left')
base['pct_escuelas_operativas'] = base['pct_escuelas_operativas'].fillna(0)
# Vulnerabilidad = escuelas SIN conectividad
base['S1_raw'] = 100 - base['pct_escuelas_operativas']
print(f"  S1 (educación): {(base['pct_escuelas_operativas']==0).sum()} distritos "
      f"sin ninguna escuela conectada "
      f"({(base['pct_escuelas_operativas']==0).sum()/len(base)*100:.1f}%)")

# ── S2: Conectividad en salud ────────────────────────────────────
sal_c = sal[['UBIGEO','pct_establecimientos_operativos']].drop_duplicates('UBIGEO')
base  = base.merge(sal_c, on='UBIGEO', how='left')
base['pct_establecimientos_operativos'] = base['pct_establecimientos_operativos'].fillna(0)
base['S2_raw'] = 100 - base['pct_establecimientos_operativos']
print(f"  S2 (salud):     {(base['pct_establecimientos_operativos']==0).sum()} distritos "
      f"sin ningún establecimiento conectado "
      f"({(base['pct_establecimientos_operativos']==0).sum()/len(base)*100:.1f}%)")

# ── S3: Capacidad digital municipal ──────────────────────────────
ren_c = ren[['UBIGEO','calidad_conexion']].drop_duplicates('UBIGEO')
base  = base.merge(ren_c, on='UBIGEO', how='left')
base['calidad_conexion'] = base['calidad_conexion'].fillna(0)
# Invertir: 5-calidad → mayor valor = mayor vulnerabilidad
base['S3_raw'] = 5 - base['calidad_conexion']
conn_labels = {0:'Sin internet',1:'Móvil',2:'Satelital',
               3:'Wi-fi',4:'ADSL',5:'Fibra'}
print(f"  S3 (municipio): distribución calidad:")
for k,v in base['calidad_conexion'].value_counts().sort_index().items():
    print(f"    {k} - {conn_labels[k]:12s}: {v:4d} ({v/len(base)*100:.1f}%)")

# ── S4: Presencia policial conectada ─────────────────────────────
dep_c = dep[['UBIGEO','tiene_dependencia_policial',
             'dependencias_operativas','pct_operativas']].drop_duplicates('UBIGEO')
base  = base.merge(dep_c, on='UBIGEO', how='left')
base['tiene_dependencia_policial'] = base['tiene_dependencia_policial'].fillna(0)
base['dependencias_operativas']    = pd.to_numeric(
    base['dependencias_operativas'], errors='coerce').fillna(0)
base['pct_operativas']             = pd.to_numeric(
    base['pct_operativas'], errors='coerce')

# S4: si no tiene dependencia = máxima vulnerabilidad (100)
# si tiene pero 0% operativas = también alta (100)
# si tiene y % operativas > 0 = 100 - pct_operativas
def calcular_s4(row):
    if row['tiene_dependencia_policial'] == 0:
        return 100.0   # sin presencia = máximo vulnerable
    elif pd.isna(row['pct_operativas']):
        return 100.0
    else:
        return 100.0 - row['pct_operativas']

base['S4_raw'] = base.apply(calcular_s4, axis=1)
sin_dep = (base['tiene_dependencia_policial']==0).sum()
print(f"  S4 (seguridad): {sin_dep} distritos sin dependencia policial "
      f"({sin_dep/len(base)*100:.1f}%)")
con_dep_op = ((base['tiene_dependencia_policial']==1) &
              (base['pct_operativas']>0)).sum()
print(f"    {con_dep_op} con al menos una dependencia operativa")

# ================================================================
# 3. NORMALIZACIÓN MIN-MAX
# ================================================================
print("\n" + "=" * 65)
print("PASO 3 — Normalización min-max [0,1]")
print("=" * 65)

scaler = MinMaxScaler()
cols_raw  = ['pct_sin_cobertura','S1_raw','S2_raw','S3_raw','S4_raw']
cols_norm = ['BASE_norm','S1_norm','S2_norm','S3_norm','S4_norm']
base[cols_norm] = scaler.fit_transform(base[cols_raw])

for raw, norm in zip(cols_raw, cols_norm):
    labels = {'pct_sin_cobertura':'BASE señal',
              'S1_raw':'S1 educación',
              'S2_raw':'S2 salud',
              'S3_raw':'S3 municipio',
              'S4_raw':'S4 seguridad'}
    print(f"  {labels[raw]:15s}: "
          f"min={base[norm].min():.3f}  "
          f"max={base[norm].max():.3f}  "
          f"media={base[norm].mean():.3f}  "
          f"std={base[norm].std():.3f}")

# ================================================================
# 4. CÁLCULO DEL IVDC v2
# ================================================================
print("\n" + "=" * 65)
print("PASO 4 — Cálculo IVDC v2")
print("=" * 65)

# Promedio simple de los 4 índices sectoriales
base['IVDC_sectorial'] = (base['S1_norm'] + base['S2_norm'] +
                           base['S3_norm'] + base['S4_norm']) / 4

# Penalidad base: si BASE_norm > 0.5 (señal muy limitada),
# amplifica la vulnerabilidad sectorial proporcionalmente
# IVDC_v2 = IVDC_sectorial * (1 + 0.3 * BASE_norm)
# Esto preserva la interpretación sectorial pero penaliza
# distritos donde ni siquiera hay señal base para ningún servicio
base['IVDC_v2'] = base['IVDC_sectorial'] * (1 + 0.3 * base['BASE_norm'])

# Renormalizar IVDC_v2 a [0,1]
ivdc_min = base['IVDC_v2'].min()
ivdc_max = base['IVDC_v2'].max()
base['IVDC_v2'] = (base['IVDC_v2'] - ivdc_min) / (ivdc_max - ivdc_min)

# Quintiles
base['quintil_ivdc_v2'] = pd.qcut(
    base['IVDC_v2'], q=5, labels=[1,2,3,4,5]).astype(int)

print(f"  IVDC_v2: min={base['IVDC_v2'].min():.4f}  "
      f"max={base['IVDC_v2'].max():.4f}  "
      f"media={base['IVDC_v2'].mean():.4f}  "
      f"std={base['IVDC_v2'].std():.4f}")
print(f"\n  Distribución por quintil:")
for q, n in base['quintil_ivdc_v2'].value_counts().sort_index().items():
    print(f"    Q{q}: {n:4d} distritos ({n/len(base)*100:.1f}%)")

print(f"\n  Top 15 distritos más vulnerables:")
top15 = base.nlargest(15,'IVDC_v2')[
    ['NOM_DPTO','NOM_DIST','IVDC_v2',
     'BASE_norm','S1_norm','S2_norm','S3_norm','S4_norm','IDH_num']]
for _, r in top15.iterrows():
    print(f"    {r['NOM_DIST']:20s} ({r['NOM_DPTO']:12s}) "
          f"IVDC={r['IVDC_v2']:.3f} "
          f"BASE={r['BASE_norm']:.2f} "
          f"S1={r['S1_norm']:.2f} "
          f"S2={r['S2_norm']:.2f} "
          f"S3={r['S3_norm']:.2f} "
          f"S4={r['S4_norm']:.2f} "
          f"IDH={r['IDH_num']:.3f}")

# ================================================================
# 5. CORRELACIONES SECTORIALES
# ================================================================
print("\n" + "=" * 65)
print("PASO 5 — Correlaciones sectoriales con outcomes del IDH")
print("=" * 65)

df_val = base.dropna(subset=['IDH_num','anios_educacion',
                               'esperanza_vida','ingreso_per_capita'])

correlaciones = {
    'IVDC_v2 ↔ IDH':            ('IVDC_v2',    'IDH_num'),
    'S1 educación ↔ años educ': ('S1_norm',    'anios_educacion'),
    'S2 salud ↔ esperanza vida':('S2_norm',    'esperanza_vida'),
    'S3 municipio ↔ ingreso':   ('S3_norm',    'ingreso_per_capita'),
    'S4 seguridad ↔ IDH':       ('S4_norm',    'IDH_num'),
    'BASE señal ↔ IDH':         ('BASE_norm',  'IDH_num'),
}

resultados_corr = {}
for label, (col_x, col_y) in correlaciones.items():
    sub = df_val[[col_x, col_y]].dropna()
    pr, pp = stats.pearsonr(sub[col_x], sub[col_y])
    sr, sp = stats.spearmanr(sub[col_x], sub[col_y])
    resultados_corr[label] = {
        'pearson_r': round(pr,4), 'pearson_p': pp,
        'spearman_r': round(sr,4), 'spearman_p': sp,
        'n': len(sub), 'col_x': col_x, 'col_y': col_y
    }
    sig = "***" if pp < 0.001 else ("**" if pp < 0.01 else "*")
    print(f"\n  {label}")
    print(f"    Pearson:  r={pr:+.4f}  p={pp:.2e} {sig}")
    print(f"    Spearman: r={sr:+.4f}  p={sp:.2e}")
    print(f"    n={len(sub)}")

# IDH promedio por quintil IVDC_v2
print(f"\n  IDH promedio por quintil IVDC_v2 (debe ser decreciente):")
tabla_q = df_val.groupby('quintil_ivdc_v2')['IDH_num'].agg(
    n='count', media='mean', minimo='min', maximo='max').round(4)
print(tabla_q.to_string())

# ================================================================
# 6. ESTADÍSTICOS POR SECTOR
# ================================================================
print("\n" + "=" * 65)
print("PASO 6 — Estadísticos por sector (para el documento)")
print("=" * 65)

# S1 Educación
print("\nS1 — EDUCACIÓN:")
print(f"  Distritos sin ninguna escuela conectada: "
      f"{(base['pct_escuelas_operativas']==0).sum()} "
      f"({(base['pct_escuelas_operativas']==0).sum()/len(base)*100:.1f}%)")
print(f"  Distritos con >50% escuelas conectadas: "
      f"{(base['pct_escuelas_operativas']>50).sum()}")
print(f"  % escuelas conectadas promedio nacional: "
      f"{base['pct_escuelas_operativas'].mean():.1f}%")
esc_dept = base.groupby('NOM_DPTO')['pct_escuelas_operativas'].mean()
print(f"  Dpto con mayor conectividad escolar: "
      f"{esc_dept.idxmax()} ({esc_dept.max():.1f}%)")
print(f"  Dpto con menor conectividad escolar: "
      f"{esc_dept.idxmin()} ({esc_dept.min():.1f}%)")

# S2 Salud
print("\nS2 — SALUD:")
print(f"  Distritos sin ningún establecimiento conectado: "
      f"{(base['pct_establecimientos_operativos']==0).sum()} "
      f"({(base['pct_establecimientos_operativos']==0).sum()/len(base)*100:.1f}%)")
print(f"  Distritos con >50% establecimientos conectados: "
      f"{(base['pct_establecimientos_operativos']>50).sum()}")
sal_dept = base.groupby('NOM_DPTO')['pct_establecimientos_operativos'].mean()
print(f"  Dpto con mayor conectividad en salud: "
      f"{sal_dept.idxmax()} ({sal_dept.max():.1f}%)")
print(f"  Dpto con menor conectividad en salud: "
      f"{sal_dept.idxmin()} ({sal_dept.min():.1f}%)")

# S3 Municipio
print("\nS3 — MUNICIPIO:")
precaria = base['calidad_conexion'].isin([0,1,2]).sum()
print(f"  Municipios sin internet o conexión precaria: "
      f"{precaria} ({precaria/len(base)*100:.1f}%)")
print(f"  Municipios con fibra óptica: "
      f"{(base['calidad_conexion']==5).sum()} "
      f"({(base['calidad_conexion']==5).sum()/len(base)*100:.1f}%)")
mun_dept = base.groupby('NOM_DPTO')['calidad_conexion'].mean()
print(f"  Dpto con mejor capacidad municipal: "
      f"{mun_dept.idxmax()} (media={mun_dept.max():.2f}/5)")
print(f"  Dpto con peor capacidad municipal: "
      f"{mun_dept.idxmin()} (media={mun_dept.min():.2f}/5)")

# S4 Seguridad
print("\nS4 — SEGURIDAD:")
sin_dep = (base['tiene_dependencia_policial']==0).sum()
print(f"  Distritos sin dependencia policial: "
      f"{sin_dep} ({sin_dep/len(base)*100:.1f}%)")
con_op = ((base['tiene_dependencia_policial']==1) &
          (base['pct_operativas']>0)).sum()
print(f"  Distritos con al menos una dependencia operativa: {con_op}")
print(f"  Distritos con dependencia pero 0% operativas: "
      f"{((base['tiene_dependencia_policial']==1) & (base['pct_operativas']==0)).sum()}")
seg_dept = base.groupby('NOM_DPTO')['tiene_dependencia_policial'].mean()*100
print(f"  Dpto con mayor cobertura policial: "
      f"{seg_dept.idxmax()} ({seg_dept.max():.1f}%)")
print(f"  Dpto con menor cobertura policial: "
      f"{seg_dept.idxmin()} ({seg_dept.min():.1f}%)")

# ================================================================
# 7. OUTPUTS
# ================================================================
print("\n" + "=" * 65)
print("PASO 7 — Generando archivos de salida")
print("=" * 65)

# ── Archivo 1: CSV distrital final ──
cols_final = [
    'UBIGEO','NOM_DPTO','NOM_PROV','NOM_DIST',
    # Índice base
    'pct_sin_cobertura','BASE_norm',
    # Índices sectoriales raw y normalizados
    'pct_escuelas_operativas','S1_raw','S1_norm',
    'pct_establecimientos_operativos','S2_raw','S2_norm',
    'calidad_conexion','S3_raw','S3_norm',
    'tiene_dependencia_policial','pct_operativas','S4_raw','S4_norm',
    # IVDC final
    'IVDC_sectorial','IVDC_v2','quintil_ivdc_v2',
    # Outcomes IDH
    'IDH','quintil_idh','ingreso_per_capita','esperanza_vida','anios_educacion',
    'IDH_num'
]
final_df = base[cols_final].copy()
for c in ['BASE_norm','S1_norm','S2_norm','S3_norm','S4_norm',
          'IVDC_sectorial','IVDC_v2','S1_raw','S2_raw','S3_raw','S4_raw']:
    final_df[c] = final_df[c].round(6)

ruta1 = OUT_DIR + "ivdc_v2_distrital_final.csv"
final_df.to_csv(ruta1, index=False, encoding='utf-8-sig')
print(f"  [OK] {ruta1}  ({len(final_df)} filas, {len(final_df.columns)} columnas)")

# ── Archivo 2: tabla departamental ──
base['IDH_num2'] = base['IDH_num']
tabla_dpto = base.groupby('NOM_DPTO').agg(
    n_distritos         = ('UBIGEO','count'),
    # Base
    pct_sin_cobertura_prom = ('pct_sin_cobertura','mean'),
    # S1
    pct_escuelas_op_prom   = ('pct_escuelas_operativas','mean'),
    s1_prom                = ('S1_norm','mean'),
    # S2
    pct_salud_op_prom      = ('pct_establecimientos_operativos','mean'),
    s2_prom                = ('S2_norm','mean'),
    # S3
    calidad_mun_prom       = ('calidad_conexion','mean'),
    s3_prom                = ('S3_norm','mean'),
    # S4
    pct_con_policia        = ('tiene_dependencia_policial','mean'),
    s4_prom                = ('S4_norm','mean'),
    # IVDC
    ivdc_prom              = ('IVDC_v2','mean'),
    ivdc_max               = ('IVDC_v2','max'),
    n_q5                   = ('quintil_ivdc_v2', lambda x: (x==5).sum()),
    # Outcomes
    idh_prom               = ('IDH_num2','mean'),
    educ_prom              = ('anios_educacion','mean'),
    salud_prom             = ('esperanza_vida','mean'),
    ingreso_prom           = ('ingreso_per_capita','mean'),
).reset_index()

tabla_dpto['pct_q5'] = (tabla_dpto['n_q5'] /
                         tabla_dpto['n_distritos'] * 100).round(1)
tabla_dpto['pct_con_policia'] = (tabla_dpto['pct_con_policia'] * 100).round(1)
for c in ['pct_sin_cobertura_prom','pct_escuelas_op_prom','s1_prom',
          'pct_salud_op_prom','s2_prom','calidad_mun_prom','s3_prom',
          's4_prom','ivdc_prom','ivdc_max','idh_prom','educ_prom',
          'salud_prom','ingreso_prom']:
    tabla_dpto[c] = tabla_dpto[c].round(3)
tabla_dpto = tabla_dpto.sort_values('ivdc_prom', ascending=False)

ruta2 = OUT_DIR + "ivdc_v2_tabla_departamental.csv"
tabla_dpto.to_csv(ruta2, index=False, encoding='utf-8-sig')
print(f"  [OK] {ruta2}  ({len(tabla_dpto)} filas)")
print(f"\n  Top 10 departamentos más vulnerables:")
print(tabla_dpto.head(10)[
    ['NOM_DPTO','n_distritos','ivdc_prom','idh_prom',
     's1_prom','s2_prom','s3_prom','s4_prom','n_q5','pct_q5']
].to_string(index=False))

# ── Archivo 3: reporte metodológico ──
corr_texto = ""
for label, r in resultados_corr.items():
    sig = "***" if r['pearson_p'] < 0.001 else ("**" if r['pearson_p'] < 0.01 else "*")
    corr_texto += (f"\n  {label}\n"
                   f"    Pearson:  r={r['pearson_r']:+.4f}  "
                   f"p={r['pearson_p']:.2e} {sig}\n"
                   f"    Spearman: r={r['spearman_r']:+.4f}  "
                   f"p={r['spearman_p']:.2e}\n"
                   f"    n={r['n']}\n")

reporte = f"""
REPORTE METODOLÓGICO — IVDC v2 Geotón Perú 2026
================================================
Fecha: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
Universo: {len(base)} distritos

═══════════════════════════════════════════════
ARQUITECTURA DEL ÍNDICE v2
═══════════════════════════════════════════════

Estructura: 1 índice base + 4 índices sectoriales

  BASE — Cobertura de señal móvil (OSIPTEL)
    Variable: % centros poblados sin cobertura
    Rol: prerequisito y amplificador de vulnerabilidad
    Actor: MTC/OSIPTEL
    Promedio nacional: {base['pct_sin_cobertura'].mean():.1f}%

  S1 — Conectividad educativa (PRONATEL/escuelas)
    Variable: % escuelas SIN conectividad operativa
    Actor: MINEDU + PRONATEL
    Implicancia: aula digital, PerúEduca, capacitación docente remota
    Sin ninguna escuela conectada: {(base['pct_escuelas_operativas']==0).sum()} distritos

  S2 — Conectividad en salud (PRONATEL/establecimientos)
    Variable: % establecimientos SIN conectividad operativa
    Actor: MINSA + PRONATEL
    Implicancia: telemedicina, HIS digital, abastecimiento farmacéutico
    Sin ningún establecimiento conectado: {(base['pct_establecimientos_operativos']==0).sum()} distritos

  S3 — Capacidad digital municipal (RENAMU)
    Variable: calidad de conexión municipal (0-5, invertido)
    Actor: PCM + MEF
    Implicancia: SIAF, SIGA, trámites digitales ciudadanos
    Sin internet o conexión precaria: {base['calidad_conexion'].isin([0,1,2]).sum()} municipios

  S4 — Presencia policial conectada (PRONATEL/PNP)
    Variable: ausencia/estado de dependencias policiales
    Actor: MININTER + PRONATEL
    Implicancia: denuncias digitales, coordinación operativa
    Sin dependencia policial: {(base['tiene_dependencia_policial']==0).sum()} distritos

═══════════════════════════════════════════════
FÓRMULA DE CÁLCULO
═══════════════════════════════════════════════

  1. Normalización min-max [0,1] de cada componente
     (mayor valor = mayor vulnerabilidad en todos los casos)

  2. Promedio sectorial:
     IVDC_sectorial = (S1_norm + S2_norm + S3_norm + S4_norm) / 4

  3. Penalidad base (amplificador):
     IVDC_v2_raw = IVDC_sectorial × (1 + 0.30 × BASE_norm)
     Interpretación: distritos sin señal reciben hasta +30%
     de penalidad sobre su vulnerabilidad sectorial.

  4. Renormalización final a [0,1]:
     IVDC_v2 = (IVDC_v2_raw - min) / (max - min)

  5. Quintiles: 1=menos vulnerable, 5=más vulnerable

═══════════════════════════════════════════════
ESTADÍSTICOS NACIONALES
═══════════════════════════════════════════════

  IVDC_v2: media={base['IVDC_v2'].mean():.4f}  std={base['IVDC_v2'].std():.4f}
  Distritos en quintil 5 (más vulnerables): {(base['quintil_ivdc_v2']==5).sum()}

  IDH promedio por quintil IVDC_v2:
{tabla_q.to_string()}

═══════════════════════════════════════════════
CORRELACIONES SECTORIALES CON OUTCOMES DEL IDH
═══════════════════════════════════════════════
{corr_texto}
Interpretación: correlaciones negativas indican que mayor
vulnerabilidad digital se asocia con menores outcomes de
desarrollo humano. No implica causalidad, sino coherencia
del instrumento como diagnóstico de capacidad de entrega
de servicios.

═══════════════════════════════════════════════
LIMITACIONES METODOLÓGICAS
═══════════════════════════════════════════════

1. TEMPORALIDAD: IDH=2019, PRONATEL=2022, OSIPTEL=2025,
   RENAMU=2025. Correlaciones son estructurales, no causales.

2. S4 COBERTURA PARCIAL: Solo 495/1,874 distritos tienen
   dependencia policial en la base PRONATEL. Los 1,379 sin
   presencia reciben vulnerabilidad máxima en S4, lo que
   puede sobreestimar la brecha policial en distritos rurales
   sin comisaría pero con presencia PNP no registrada en
   los proyectos PRONATEL.

3. S1 y S2 COBERTURA PRONATEL: Cubren 77-80% de distritos.
   Distritos sin presencia PRONATEL reciben valor=100%
   vulnerable en esos sectores.

4. S3 SIAF/SIGA: Variables usa_siaf y usa_siga sin varianza
   en este corte. Se usó calidad de conexión ordinal como
   proxy de capacidad operativa digital.

5. PENALIDAD BASE: El coeficiente 0.30 es conservador por
   diseño. En iteraciones futuras puede ajustarse con datos
   de año común mediante regresión OLS.

═══════════════════════════════════════════════
OUTPUTS GENERADOS
═══════════════════════════════════════════════
  1. ivdc_v2_distrital_final.csv      — {len(final_df)} filas × {len(final_df.columns)} cols
  2. ivdc_v2_tabla_departamental.csv  — 25 departamentos
  3. ivdc_v2_reporte_metodologico.txt — este archivo
"""

ruta3 = OUT_DIR + "ivdc_v2_reporte_metodologico.txt"
with open(ruta3, 'w', encoding='utf-8') as f:
    f.write(reporte)
print(f"  [OK] {ruta3}")

print("\n" + "=" * 65)
print("PROCESO COMPLETADO — IVDC v2 Sectorial")
print("=" * 65)
