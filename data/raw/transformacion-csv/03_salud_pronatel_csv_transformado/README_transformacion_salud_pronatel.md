# Transformación a CSV - Establecimientos de salud PRONATEL febrero 2022

## Dataset procesado
Archivo shapefile base: `peru_infraestructura_estable_salud_pronatel_feb2022_.shp`

Este paquete corresponde a establecimientos de salud asociados a proyectos/intervenciones de PRONATEL, con ubicación puntual y estado operativo reportado a febrero de 2022.

## Archivos generados

1. `salud_pronatel_atributos.csv`  
   CSV principal para análisis tabular. Una fila representa un establecimiento de salud o punto beneficiario.

2. `salud_pronatel_completo_con_geometria_wkt.csv`  
   Contiene los mismos atributos y la columna `geometry_wkt` para conservar la geometría en formato texto espacial.

3. `salud_pronatel_diccionario_variables.csv`  
   Diccionario de variables con significado, tipo de dato, nulos, valores únicos, mínimos/máximos, ejemplos y observaciones.

4. `salud_pronatel_resumen_calidad.csv`  
   Controles de calidad aplicados durante la transformación.

5. `salud_pronatel_resumen_por_departamento.csv`  
   Agregación de establecimientos por departamento.

6. `salud_pronatel_resumen_por_estado.csv`  
   Distribución por estado operativo.

7. `salud_pronatel_resumen_por_proyecto.csv`  
   Agregación por proyecto/intervención PRONATEL.

8. `salud_pronatel_resumen_por_distrito.csv`  
   Agregación territorial distrital usando `UBIGEO` / `COD_DIST`.

## Validaciones principales

- Registros leídos: 3,904
- Campos originales DBF: 23
- CRS: EPSG:4326
- EPSG: 4326
- Encoding declarado: UTF-8
- Tipo de geometría: Point
- Geometrías nulas: 0
- Geometrías vacías: 0
- Geometrías inválidas: 0
- Coordenadas fuera del rango aproximado de Perú: 0
- Duplicados exactos sin geometría: 0
- Duplicados por clave establecimiento + CCPP + distrito + nombre: 0

## Variables clave para GEOTÓN

- `UBIGEO` / `COD_DIST`: permiten cruzar el dataset con indicadores distritales como IDH, pobreza, cobertura móvil u otros.
- `COD_CCPP`, `NOM_CCPP`, `IDCCPP`: permiten análisis a nivel de centro poblado cuando exista compatibilidad con otros datasets.
- `NOM_EST_SL`, `COD_EST_SL`: identifican el establecimiento de salud.
- `ESTADO`, `COD_EST`: indican si el establecimiento figura operativo o no operativo.
- `NOM_PROY`: proyecto o intervención PRONATEL asociada.
- `XCENT`, `YCENT`, `geom_lon`, `geom_lat`: coordenadas en WGS84.

## Recomendaciones de uso

- Tratar `COD_DPTO`, `COD_PROV`, `COD_DIST`, `COD_CCPP`, `IDCCPP` y `UBIGEO` como texto para no perder ceros iniciales.
- Usar `salud_pronatel_atributos.csv` para análisis tabular y dashboards.
- Usar `salud_pronatel_completo_con_geometria_wkt.csv` si se necesita cargar la geometría en una herramienta SIG o base espacial.
- Antes de tomar decisiones oficiales, contrastar con la fuente proveedora porque GEOPERÚ publica los datos como información de apoyo y no como certificación oficial.
