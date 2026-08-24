-- Migración v5 — UrbanStyle
-- Aplicar sobre la BD ya migrada con migracion_v4.sql
-- Objetivo: gestión de estados de pedidos, envíos y anulaciones.
--
-- `facturas.estado` pasa de enum('activa','anulada') a
-- enum('pendiente','enviado','entregado','anulado'):
--   pendiente  -> pedido pagado, aun no despachado (estado inicial)
--   enviado    -> el admin despacho el pedido
--   entregado  -> el pedido llego al cliente
--   anulado    -> pedido cancelado (por el admin o por el cliente
--                 dentro de los primeros 30 minutos); restaura el stock

-- 1) se amplia el enum sin perder los valores viejos, para poder
--    migrar los datos existentes sin romper filas.
ALTER TABLE `facturas`
  MODIFY `estado` enum('activa','anulada','pendiente','enviado','entregado','anulado')
  DEFAULT 'pendiente';

-- 2) se traducen los valores viejos a los nuevos
UPDATE `facturas` SET `estado` = 'pendiente' WHERE `estado` = 'activa';
UPDATE `facturas` SET `estado` = 'anulado' WHERE `estado` = 'anulada';

-- 3) se deja el enum solo con los valores nuevos
ALTER TABLE `facturas`
  MODIFY `estado` enum('pendiente','enviado','entregado','anulado')
  DEFAULT 'pendiente';
