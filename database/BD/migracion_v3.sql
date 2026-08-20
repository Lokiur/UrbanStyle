-- Migración v3 — UrbanStyle
-- Aplicar sobre la BD ya migrada con migracion_v2.sql
-- Objetivo: permitir que cada usuario suba una foto de perfil.

ALTER TABLE `users`
  ADD COLUMN `avatar` VARCHAR(255) DEFAULT NULL AFTER `celular`;
