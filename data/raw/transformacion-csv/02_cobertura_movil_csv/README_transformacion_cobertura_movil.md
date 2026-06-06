# Transformación a CSV - Cobertura móvil por centro poblado

## Fuente y archivos de entrada

Paquete shapefile descargado desde GEOPERÚ:

- `20250901151931___Capa5_CCPP_Cob_1er_Trim_2025.shp`
- `20250901151931___Capa5_CCPP_Cob_1er_Trim_2025.shx`
- `20250901151931___Capa5_CCPP_Cob_1er_Trim_2025.dbf`
- `20250901151931___Capa5_CCPP_Cob_1er_Trim_2025.prj`
- `20250901151931___Capa5_CCPP_Cob_1er_Trim_2025.qix`
- `readme.pdf` con aviso legal de GEOPERÚ.

## Resultado

Se generaron archivos separados para mantener la data ordenada, auditable y menos propensa a errores:

1. `cobertura_movil_ccpp_atributos.csv`
   - Tabla principal para análisis.
   - Una fila representa un centro poblado.
   - Incluye atributos originales y coordenadas derivadas desde la geometría.

2. `cobertura_movil_ccpp_completo_con_geometria_wkt.csv`
   - Versión completa con `geometry_wkt`.
   - Útil si luego se desea reconstruir la capa espacial desde CSV.

3. `cobertura_movil_ccpp_diccionario_variables.csv`
   - Diccionario técnico de variables.
   - Incluye significado, tipo DBF, nulos, únicos, mínimo, máximo y observaciones.

4. `cobertura_movil_ccpp_resumen_calidad.csv`
   - Controles de calidad aplicados durante la transformación.

5. `cobertura_movil_resumen_por_departamento.csv`
   - Resumen agregado por departamento para análisis rápido.

## Controles principales

- Registros leídos: 108,115
- Campos originales DBF: 31
- Tipo de geometría: POINT
- CRS leído del `.prj`: GCS_WGS_1984 / WGS84 geographic coordinates
- EPSG estimado: EPSG:4326
- Encoding usado: UTF-8
- Geometrías vacías: 0
- Coordenadas fuera de rango aproximado de Perú: 0
- Diferencias entre LONG_X/LAT_Y y geometría: 0
- Duplicados por nombre + coordenada: 5

## Recomendaciones de uso

- Usar `cobertura_movil_ccpp_atributos.csv` para Excel, Google Sheets, Power BI o análisis tabular.
- Usar `cobertura_movil_ccpp_completo_con_geometria_wkt.csv` solo cuando se requiera reconstruir geometría espacial.
- Mantener códigos como texto, aunque en esta descarga `COD_DPTO`, `COD_PROV`, `COD_DIST` e `IDCCPP` aparecen vacíos.
- Para análisis del proyecto GEOTÓN, esta capa sirve para medir presencia o ausencia de cobertura móvil por centro poblado y por operador.

## Nota metodológica

`COB_TOTAL` debe interpretarse como indicador general de cobertura móvil en el centro poblado. Para evaluar brechas territoriales, se recomienda analizar también la diferencia entre zonas urbanas y rurales (`CLASIFIC`) y revisar cobertura por operador (`COB_BIT`, `COB_CLARO`, `COB_ENTEL`, `COB_MOVIS`).
