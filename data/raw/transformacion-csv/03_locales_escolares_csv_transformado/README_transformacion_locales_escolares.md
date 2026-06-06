# Transformación a CSV - Locales escolares PRONATEL febrero 2022

## Archivos fuente
- Shapefile: `peru_infraestructura_loc_esc_pron_feb2022_.shp`
- Índice: `.shx`
- Tabla de atributos: `.dbf`
- Proyección: `.prj`
- Encoding: `.cpg`
- Estilo: `.sld`
- Aviso legal GEOPERÚ: `readme.pdf`

## Resultado
Se generaron archivos CSV separados para mantener el dataset ordenado, auditable y menos propenso a errores:

1. `locales_escolares_atributos.csv`: tabla principal sin geometría WKT pesada.
2. `locales_escolares_completo_con_geometria_wkt.csv`: tabla completa con geometría en WKT.
3. `locales_escolares_diccionario_variables.csv`: diccionario técnico de variables.
4. `locales_escolares_resumen_calidad.csv`: controles de transformación y calidad.
5. `locales_escolares_resumen_por_departamento.csv`: agregación territorial para análisis.
6. `locales_escolares_resumen_por_estado.csv`: conteo por estado operativo.
7. `locales_escolares_resumen_por_proyecto.csv`: agregación por proyecto/intervención.

## Validaciones principales
- Registros leídos: 8,720
- Campos originales DBF: 22
- CRS detectado: EPSG:4326
- EPSG: 4326
- Encoding declarado: UTF-8
- Tipo de geometría: Point
- Geometrías nulas: 0
- Geometrías vacías: 0
- Geometrías inválidas: 0
- Coordenadas fuera del rango aproximado de Perú: 0
- Filas duplicadas exactas en atributos derivados: 0
- Filas con la misma combinación local escolar + centro poblado + territorio: 83

## Distribución por estado
{
  "NO OPERATIVO": 5740,
  "OPERATIVO": 2980
}

## Variables clave para GEOTÓN
- `COD_DPTO`, `COD_PROV`, `COD_DIST`: códigos territoriales para cruces por departamento, provincia y distrito.
- `COD_CCPP`, `NOM_CCPP`: centro poblado asociado.
- `NOM_LOC_ES`, `COD_LOC_ES`: local escolar.
- `NOM_PROY`: proyecto o intervención PRONATEL.
- `ESTADO`, `COD_ESTADO`: situación operativa del local escolar.
- `XCENT_CCPP`, `YCENT_CCPP`, `geom_lon`, `geom_lat`: coordenadas geográficas.

## Notas técnicas
- Los códigos territoriales y códigos de centro poblado deben tratarse como texto para conservar ceros iniciales.
- La geometría fue exportada como WKT en el archivo completo para permitir reutilización en herramientas GIS o bases espaciales.
- El archivo principal de atributos es más liviano y recomendable para Excel, Power BI, Google Sheets y análisis tabular.
- El aviso legal de GEOPERÚ indica que la plataforma sirve para fines informativos, técnicos, investigación y análisis territorial; también advierte que la entidad proveedora es responsable de la calidad y actualización de los datos.
