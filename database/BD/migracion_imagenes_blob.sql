-- Migración: almacenar la imagen de cada producto directamente en la base de datos (BLOB)
-- Reemplaza la columna `imagen_ruta` (no usada por el código, con datos obsoletos)
-- por `imagen` (contenido binario) e `imagen_mime` (tipo de contenido, ej. image/jpeg).

ALTER TABLE productos
  DROP COLUMN imagen_ruta,
  ADD COLUMN imagen LONGBLOB NULL AFTER descripcion,
  ADD COLUMN imagen_mime VARCHAR(100) NULL AFTER imagen;
