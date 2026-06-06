# Transformación a CSV - Dependencias policiales Perú, febrero 2022

## Dataset procesado

Capa geográfica: `peru_infraestructura_dependencias_policiales_feb2022_`.

La capa contiene puntos de dependencias policiales, con ubicación territorial, estado operativo, nombre de la dependencia y fuente institucional.

## Archivos generados

1. `dependencias_policiales_atributos.csv`: tabla principal para análisis. Una fila representa una dependencia policial.
2. `dependencias_policiales_completo_con_geometria_wkt.csv`: tabla completa con todos los atributos y geometría en formato WKT.
3. `dependencias_policiales_diccionario_variables.csv`: diccionario de variables con descripción, tipo de dato, nulos, únicos, mínimos/máximos y observaciones.
4. `dependencias_policiales_resumen_calidad.csv`: controles de calidad de la conversión.
5. `dependencias_policiales_resumen_por_departamento.csv`: conteo de dependencias policiales por departamento y estado operativo.
6. `dependencias_policiales_resumen_por_estado.csv`: conteo general por estado operativo.

## Validaciones realizadas

- Registros leídos: 563.
- Campos originales de atributos: 23.
- CRS: EPSG:4326.
- EPSG detectado: 4326.
- Encoding declarado: UTF-8.
- Tipo de geometría: Point: 563.
- Geometrías nulas: 0.
- Geometrías inválidas: 0.
- Coordenadas fuera del rango aproximado de Perú: 0.
- Diferencias entre `XCENT` y longitud geométrica: 0.
- Diferencias entre `YCENT` y latitud geométrica: 0.
- Fuente declarada: Ministerio de Transportes y Comunicaciones (MTC). Programa Nacional de Telecomunicaciones (PRONATEL), febrero de 2022.

## Notas de uso

- Los campos `COD_DPTO`, `COD_PROV`, `COD_DIST`, `COD_CCPP`, `IDCCPP` y `UBIGEO` deben tratarse como texto. Si se abren directamente en Excel, podrían perder ceros iniciales.
- Para cruces con otros datasets distritales, usar `UBIGEO` como llave principal.
- `COD_ESTADO` y `ESTADO` permiten distinguir dependencias operativas y no operativas. Según la simbología SLD del shapefile: `1 = OPERATIVO` y `2 = NO OPERATIVO`.
- `XCENT` y `YCENT` coinciden con la geometría del punto en esta transformación.
- La geometría original está en EPSG:4326 / WGS84.

## Relevancia para GEOTÓN

Este dataset puede servir como variable de infraestructura pública/seguridad para análisis territorial. Permite identificar distritos o departamentos con presencia de dependencias policiales y contrastarlo con conectividad, centros poblados, pobreza, IDH u otros indicadores territoriales.
