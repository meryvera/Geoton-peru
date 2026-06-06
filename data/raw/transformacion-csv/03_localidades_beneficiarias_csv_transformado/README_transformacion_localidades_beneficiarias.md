# Transformación a CSV - Localidades Beneficiarias

## Dataset procesado
- Nombre de capa: `Localidades_Beneficiarias`
- Archivo base: `20240416105813___Localidades_Beneficiarias.shp`
- Registros leídos: 6,945
- Campos originales DBF: 16
- Geometría: Point
- CRS detectado: `EPSG:4326`
- Encoding usado: UTF-8. No se recibió archivo `.cpg` en este paquete.

## Archivos generados
1. `localidades_beneficiarias_atributos.csv`: tabla principal sin geometría WKT pesada.
2. `localidades_beneficiarias_completo_con_geometria_wkt.csv`: tabla completa con geometría WKT.
3. `localidades_beneficiarias_diccionario_variables.csv`: diccionario técnico de variables.
4. `localidades_beneficiarias_resumen_calidad.csv`: controles de calidad de la transformación.
5. `localidades_beneficiarias_resumen_por_departamento.csv`: agregación territorial departamental.
6. `localidades_beneficiarias_resumen_por_estado_proyecto.csv`: agregación por estado del proyecto.
7. `localidades_beneficiarias_resumen_por_proyecto.csv`: agregación por proyecto/intervención.
8. `localidades_beneficiarias_resumen_por_distrito.csv`: agregación por distrito/UBIGEO.

## Variables clave
- `cod_dpto`, `cod_prov`, `cod_dist`, `cod_ccpp`: códigos territoriales. Deben mantenerse como texto.
- `nom_dpto`, `nom_prov`, `nom_dist`, `nom_ccpp`: nombres territoriales.
- `PY_BAN_ANC`: tipo/familia de proyecto de banda ancha.
- `NOM_PROYEC`: nombre del proyecto.
- `ESTADO_PY`: estado del proyecto.
- `POB_2023`: población reportada/estimada 2023.
- `IAOS_PY`, `IIEE_PY`, `EESS_PY`, `DP_PY`: conteos de instituciones/servicios beneficiarios asociados a la localidad.
- `geom_lon`, `geom_lat`: coordenadas extraídas de la geometría.
- `geometry_wkt`: geometría en texto espacial.

## Controles de calidad principales
- Geometrías nulas: 0
- Geometrías vacías: 0
- Geometrías inválidas: 0
- Coordenadas fuera del rango aproximado de Perú: 0
- Filas duplicadas exactas en atributos: 0
- Duplicados por código territorial de centro poblado: 0
- Localidades con `POB_2023 = 0`: 14

## Totales de referencia
- Localidades beneficiarias: 6,945
- Población 2023 total reportada: 3,260,147
- Total IAOS: 11,494
- Total IIEE: 7,670
- Total EESS: 3,470
- Total DP: 415

## Recomendaciones de uso
- Para análisis tabular, usar `localidades_beneficiarias_atributos.csv`.
- Para análisis SIG, usar `localidades_beneficiarias_completo_con_geometria_wkt.csv`.
- Para cruces con otros datasets de GEOTÓN, usar principalmente `cod_dist` como UBIGEO distrital y `cod_ccpp` cuando exista coincidencia a nivel centro poblado.
- No convertir códigos territoriales a número en Excel/Power BI porque pueden perder ceros iniciales.
- Validar con PRONATEL/MTC la definición oficial de `IAOS_PY` si el análisis requiere precisión institucional fina.

## Fuente y uso
El `readme.pdf` adjunto por GEOPERÚ indica que el uso de los datos es informativo, técnico y de apoyo al análisis territorial, y que la responsabilidad de generación, actualización, calidad y consistencia corresponde a la entidad pública proveedora.
