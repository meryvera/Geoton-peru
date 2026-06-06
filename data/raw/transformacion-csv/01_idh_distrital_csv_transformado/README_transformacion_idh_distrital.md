# Transformación a CSV - IDH distrital Perú

## Archivos generados

1. `peru_idh_distrital_atributos.csv`: tabla principal para análisis en Excel/Sheets/BI. Incluye atributos originales y variables espaciales derivadas simples, pero no incluye WKT completo para mantener un archivo liviano.
2. `peru_idh_distrital_completo_con_geometria_wkt.csv`: tabla completa con todos los atributos y la geometría distrital en formato WKT.
3. `peru_idh_distrital_diccionario_variables.csv`: diccionario de variables con descripción, tipo de dato, nulos, únicos, mínimos/máximos y observaciones de uso.
4. `peru_idh_distrital_resumen_calidad.csv`: controles de calidad de la conversión.

## Validaciones realizadas

- Registros leídos: 1874.
- Campos originales de atributos: 29.
- CRS: EPSG:4326.
- Encoding declarado: UTF-8.
- UBIGEO duplicados: 0.
- Geometrías nulas: 0.
- Geometrías inválidas: 0.
- Fuente declarada: Programa de las Naciones Unidas para el Desarrollo (PNUD), 2019. Unidad del Informe sobre Desarrollo Humano. Perú.

## Nota importante sobre Excel

Los campos `COD_DPTO`, `COD_PROV`, `COD_DIST` y `UBIGEO` deben tratarse como texto. Si se abre el CSV directamente con doble clic en Excel, Excel podría quitar ceros iniciales. Para evitarlo, importar el CSV indicando esas columnas como texto.

## Nota sobre geometría

La geometría original está en EPSG:4326. El archivo completo incluye `geometry_wkt`. Las áreas y perímetros agregados son derivados geodésicos calculados sobre WGS84 y sirven como referencia analítica.
