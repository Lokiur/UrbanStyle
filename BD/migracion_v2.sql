-- Migración v2 — UrbanStyle
-- Aplicar sobre la BD ya creada con urbanstyle.sql
-- Objetivo: soportar hash de contraseñas, evitar usuarios/emails duplicados
-- y habilitar la recuperación de contraseña por documento de identidad.

ALTER TABLE `users`
  ADD COLUMN `documento_identidad` VARCHAR(20) DEFAULT NULL AFTER `apellidos`;

ALTER TABLE `users`
  ADD UNIQUE KEY `uq_username` (`username`),
  ADD UNIQUE KEY `uq_email` (`email`);
