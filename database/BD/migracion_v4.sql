-- Migración v4 — UrbanStyle
-- Aplicar sobre la BD ya migrada con migracion_v3.sql
-- Objetivo: guardar los mensajes del formulario de Contacto para que
-- el admin pueda consultarlos desde el panel.

CREATE TABLE `mensajes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `email` varchar(120) NOT NULL,
  `mensaje` text NOT NULL,
  `estado` enum('nuevo','leido') DEFAULT 'nuevo',
  `fecha` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
