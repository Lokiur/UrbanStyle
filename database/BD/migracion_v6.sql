-- Migración v6 — UrbanStyle
-- Aplicar sobre la BD ya migrada con migracion_v5.sql
-- Objetivo: agregar la etapa "preparación" al flujo de estados de pedido.
--
-- flujo: pendiente -> preparacion -> enviado -> entregado, o anulado
-- desde pendiente, preparacion o enviado.

ALTER TABLE `facturas`
  MODIFY `estado` enum('pendiente','preparacion','enviado','entregado','anulado')
  DEFAULT 'pendiente';
