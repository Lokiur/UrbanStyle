-- Migración — UrbanStyle
-- Aplicar sobre una BD que todavía tenga `users.avatar varchar(255)`
-- (el nombre del archivo subido, guardado en disco).
--
-- Objetivo: guardar la foto de perfil como BLOB en la BD (igual que las
-- imagenes de producto/categoria), para que sobreviva a un redeploy en
-- hostings con disco efimero (Render, Railway, etc.), donde cualquier
-- archivo guardado en app/static/img/avatars se perderia.

ALTER TABLE `users`
  ADD COLUMN `avatar_imagen` longblob DEFAULT NULL AFTER `avatar`,
  ADD COLUMN `avatar_mime` varchar(100) DEFAULT NULL AFTER `avatar_imagen`;

ALTER TABLE `users` DROP COLUMN `avatar`;
