-- Ofertas: porcentaje de descuento por producto (0 = sin oferta).
-- El administrador lo asigna desde el panel (Productos > Editar) y los
-- productos con descuento aparecen en la pagina de Ofertas. El precio
-- de cada existencia no cambia: el descuento se aplica al mostrarlo y
-- al pasar el carrito a la factura.
--
-- Solo hace falta en bases creadas antes de este cambio (el volcado
-- urbanstyle.sql ya trae la columna). La app tambien la agrega sola al
-- arrancar si no existe (ver products_service.asegurar_columna_descuento).

ALTER TABLE `productos`
  ADD COLUMN `descuento` tinyint(3) UNSIGNED NOT NULL DEFAULT 0
  COMMENT 'Porcentaje de descuento (0 = sin oferta)'
  AFTER `estado`;
