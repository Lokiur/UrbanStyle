-- ============================================================
-- UrbanStyle - Script unificado de base de datos
-- Generado a partir de BD/urbanstyle.sql (estructura + datos)
-- con la migración BD/migracion_v2.sql ya aplicada
-- (columna `documento_identidad` en `users`).
--
-- NOTA: BD/urbanstyle_backup.sql NO se incluyó porque define un
-- esquema antiguo e incompatible (mismas tablas, columnas
-- distintas: sin `existencias`, `colores`, `tallas`, `marcas`,
-- `sku`, etc.). Mezclarlo con urbanstyle.sql produciría choques
-- de definición. Si en verdad necesitas restaurar esa versión
-- antigua, debe ejecutarse sola, en una base de datos vacía.
-- ============================================================

CREATE DATABASE IF NOT EXISTS `urbanstyle` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `urbanstyle`;

-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 24-07-2026 a las 21:20:49
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `urbanstyle`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carrito`
--

CREATE TABLE `carrito` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `carrito`
--

INSERT INTO `carrito` (`id`, `user_id`, `fecha`) VALUES
(1, 3, '2026-07-18 10:15:00'),
(2, 5, '2026-07-19 16:40:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id`, `nombre`) VALUES
(1, 'Camisetas'),
(4, 'Chaquetas'),
(2, 'Pantalones'),
(3, 'Sudaderas');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `colores`
--

CREATE TABLE `colores` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `colores`
--

INSERT INTO `colores` (`id`, `nombre`) VALUES
(3, 'Azul'),
(2, 'Blanco'),
(1, 'Negro'),
(4, 'Rojo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_carrito`
--

CREATE TABLE `detalle_carrito` (
  `id` int(11) NOT NULL,
  `carrito_id` int(11) NOT NULL,
  `existencia_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_carrito`
--

INSERT INTO `detalle_carrito` (`id`, `carrito_id`, `existencia_id`, `cantidad`) VALUES
(2, 1, 13, 1),
(3, 2, 21, 3),
(4, 1, 5, 2),
(6, 2, 6, 3);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_factura`
--

CREATE TABLE `detalle_factura` (
  `id` int(11) NOT NULL,
  `factura_id` int(11) NOT NULL,
  `existencia_id` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_factura`
--

INSERT INTO `detalle_factura` (`id`, `factura_id`, `existencia_id`, `cantidad`, `precio_unitario`, `subtotal`) VALUES
(1, 1, 1, 2, 85000.00, 170000.00),
(2, 1, 9, 1, 120000.00, 120000.00),
(3, 2, 17, 1, 180000.00, 180000.00),
(4, 2, 6, 2, 65000.00, 130000.00),
(5, 3, 21, 2, 70000.00, 140000.00),
(31, 12, 18, 3, 180000.00, 540000.00),
(32, 12, 6, 2, 65000.00, 130000.00),
(33, 12, 9, 1, 120000.00, 120000.00),
(34, 12, 17, 3, 180000.00, 540000.00),
(35, 13, 8, 1, 65000.00, 65000.00),
(36, 14, 8, 1, 65000.00, 65000.00),
(37, 15, 19, 1, 175000.00, 175000.00),
(38, 15, 16, 2, 105000.00, 210000.00),
(39, 16, 22, 3, 70000.00, 210000.00),
(40, 17, 18, 1, 180000.00, 180000.00),
(41, 17, 15, 2, 105000.00, 210000.00),
(42, 18, 2, 3, 85000.00, 255000.00),
(43, 19, 14, 2, 110000.00, 220000.00),
(44, 19, 16, 1, 105000.00, 105000.00),
(45, 20, 14, 3, 110000.00, 330000.00),
(46, 20, 18, 2, 180000.00, 360000.00),
(47, 20, 22, 1, 70000.00, 70000.00),
(48, 21, 2, 3, 85000.00, 255000.00),
(49, 21, 19, 3, 175000.00, 525000.00),
(50, 21, 16, 1, 105000.00, 105000.00),
(51, 22, 19, 1, 175000.00, 175000.00),
(52, 23, 9, 3, 120000.00, 360000.00),
(53, 23, 7, 2, 65000.00, 130000.00),
(54, 23, 22, 1, 70000.00, 70000.00),
(55, 24, 20, 3, 175000.00, 525000.00),
(62, 58, 16, 3, 105000.00, 315000.00),
(63, 58, 22, 2, 70000.00, 140000.00),
(64, 59, 3, 2, 85000.00, 170000.00),
(65, 59, 19, 3, 175000.00, 525000.00),
(66, 60, 6, 2, 65000.00, 130000.00),
(67, 60, 11, 1, 135000.00, 135000.00),
(68, 60, 5, 3, 90000.00, 270000.00),
(69, 60, 16, 1, 105000.00, 105000.00),
(70, 61, 19, 2, 175000.00, 350000.00),
(71, 61, 15, 3, 105000.00, 315000.00),
(72, 61, 3, 3, 85000.00, 255000.00),
(73, 61, 9, 1, 120000.00, 120000.00),
(74, 62, 22, 2, 70000.00, 140000.00),
(75, 62, 12, 1, 135000.00, 135000.00),
(76, 62, 1, 3, 85000.00, 255000.00),
(77, 62, 15, 1, 105000.00, 105000.00),
(78, 63, 8, 2, 65000.00, 130000.00),
(79, 63, 13, 2, 110000.00, 220000.00),
(80, 64, 14, 2, 110000.00, 220000.00),
(81, 64, 12, 1, 135000.00, 135000.00),
(82, 64, 22, 1, 70000.00, 70000.00),
(83, 65, 10, 2, 120000.00, 240000.00),
(84, 65, 1, 3, 85000.00, 255000.00),
(85, 65, 5, 2, 90000.00, 180000.00),
(86, 66, 15, 3, 105000.00, 315000.00),
(87, 67, 7, 2, 65000.00, 130000.00),
(88, 68, 12, 3, 135000.00, 405000.00),
(89, 69, 16, 2, 105000.00, 210000.00),
(90, 69, 4, 2, 85000.00, 170000.00),
(91, 69, 15, 2, 105000.00, 210000.00),
(92, 70, 7, 3, 65000.00, 195000.00),
(93, 71, 9, 3, 120000.00, 360000.00),
(94, 72, 20, 1, 175000.00, 175000.00),
(95, 72, 7, 2, 65000.00, 130000.00),
(96, 73, 9, 2, 120000.00, 240000.00),
(97, 73, 7, 3, 65000.00, 195000.00),
(98, 73, 20, 2, 175000.00, 350000.00),
(99, 73, 12, 2, 135000.00, 270000.00),
(100, 74, 16, 3, 105000.00, 315000.00),
(101, 75, 14, 2, 110000.00, 220000.00),
(102, 75, 21, 1, 70000.00, 70000.00),
(103, 76, 19, 3, 175000.00, 525000.00),
(104, 76, 15, 1, 105000.00, 105000.00),
(105, 77, 1, 1, 85000.00, 85000.00),
(106, 77, 21, 3, 70000.00, 210000.00),
(107, 78, 10, 1, 120000.00, 120000.00),
(108, 78, 17, 3, 180000.00, 540000.00),
(109, 79, 17, 2, 180000.00, 360000.00),
(110, 79, 5, 1, 90000.00, 90000.00),
(111, 79, 18, 3, 180000.00, 540000.00),
(112, 79, 1, 1, 85000.00, 85000.00),
(113, 80, 4, 1, 85000.00, 85000.00),
(114, 80, 18, 2, 180000.00, 360000.00),
(115, 80, 2, 1, 85000.00, 85000.00),
(116, 80, 8, 1, 65000.00, 65000.00),
(117, 81, 9, 3, 120000.00, 360000.00),
(118, 81, 15, 3, 105000.00, 315000.00),
(119, 82, 5, 2, 90000.00, 180000.00),
(120, 82, 14, 2, 110000.00, 220000.00),
(121, 82, 4, 1, 85000.00, 85000.00),
(122, 82, 13, 3, 110000.00, 330000.00),
(123, 83, 5, 1, 90000.00, 90000.00),
(124, 83, 9, 3, 120000.00, 360000.00),
(125, 83, 15, 1, 105000.00, 105000.00),
(126, 84, 11, 2, 135000.00, 270000.00),
(127, 84, 14, 1, 110000.00, 110000.00),
(128, 84, 7, 3, 65000.00, 195000.00),
(129, 84, 12, 2, 135000.00, 270000.00),
(130, 85, 17, 1, 180000.00, 180000.00),
(131, 85, 3, 1, 85000.00, 85000.00),
(132, 85, 4, 1, 85000.00, 85000.00),
(133, 86, 13, 3, 110000.00, 330000.00),
(134, 86, 5, 3, 90000.00, 270000.00),
(135, 86, 18, 2, 180000.00, 360000.00),
(136, 87, 9, 1, 120000.00, 120000.00),
(137, 88, 20, 3, 175000.00, 525000.00),
(138, 88, 5, 3, 90000.00, 270000.00),
(139, 88, 2, 1, 85000.00, 85000.00),
(140, 89, 10, 3, 120000.00, 360000.00),
(141, 89, 15, 3, 105000.00, 315000.00),
(142, 90, 17, 3, 180000.00, 540000.00),
(143, 91, 22, 3, 70000.00, 210000.00),
(144, 91, 16, 2, 105000.00, 210000.00),
(145, 91, 18, 3, 180000.00, 540000.00),
(146, 91, 13, 1, 110000.00, 110000.00),
(147, 92, 5, 1, 90000.00, 90000.00),
(148, 93, 17, 1, 180000.00, 180000.00),
(149, 93, 22, 3, 70000.00, 210000.00),
(150, 93, 10, 2, 120000.00, 240000.00),
(151, 93, 20, 1, 175000.00, 175000.00),
(152, 94, 1, 3, 85000.00, 255000.00),
(153, 94, 9, 2, 120000.00, 240000.00),
(154, 94, 12, 1, 135000.00, 135000.00),
(155, 94, 11, 1, 135000.00, 135000.00),
(156, 95, 8, 1, 65000.00, 65000.00),
(157, 95, 17, 1, 180000.00, 180000.00),
(158, 96, 3, 3, 85000.00, 255000.00),
(159, 96, 19, 1, 175000.00, 175000.00),
(160, 97, 2, 3, 85000.00, 255000.00),
(161, 97, 17, 2, 180000.00, 360000.00),
(162, 98, 3, 1, 85000.00, 85000.00),
(163, 98, 1, 1, 85000.00, 85000.00),
(164, 99, 16, 1, 105000.00, 105000.00),
(165, 99, 9, 2, 120000.00, 240000.00),
(166, 100, 16, 2, 105000.00, 210000.00),
(167, 101, 16, 3, 105000.00, 315000.00),
(168, 102, 9, 3, 120000.00, 360000.00),
(169, 102, 21, 3, 70000.00, 210000.00),
(170, 102, 10, 1, 120000.00, 120000.00),
(171, 103, 22, 2, 70000.00, 140000.00),
(172, 103, 16, 3, 105000.00, 315000.00),
(173, 104, 4, 1, 85000.00, 85000.00),
(174, 104, 18, 2, 180000.00, 360000.00),
(175, 104, 7, 1, 65000.00, 65000.00),
(176, 104, 10, 2, 120000.00, 240000.00),
(177, 105, 7, 3, 65000.00, 195000.00),
(178, 105, 3, 3, 85000.00, 255000.00),
(179, 105, 19, 2, 175000.00, 350000.00),
(180, 105, 5, 2, 90000.00, 180000.00),
(181, 106, 16, 1, 105000.00, 105000.00),
(182, 106, 13, 2, 110000.00, 220000.00),
(183, 106, 1, 3, 85000.00, 255000.00),
(184, 106, 6, 2, 65000.00, 130000.00),
(185, 107, 1, 1, 85000.00, 85000.00),
(186, 107, 11, 1, 135000.00, 135000.00),
(187, 107, 13, 3, 110000.00, 330000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `direcciones`
--

CREATE TABLE `direcciones` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `direccion` varchar(255) NOT NULL,
  `ciudad` varchar(100) DEFAULT NULL,
  `departamento` varchar(100) DEFAULT NULL,
  `codigo_postal` varchar(20) DEFAULT NULL,
  `principal` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `direcciones`
--

INSERT INTO `direcciones` (`id`, `user_id`, `direccion`, `ciudad`, `departamento`, `codigo_postal`, `principal`) VALUES
(1, 2, 'Calle 123 #45-67', 'Bogotá', 'Cundinamarca', '110111', 1),
(2, 3, 'Carrera 45 #12-34', 'Medellín', 'Antioquia', '050001', 1),
(3, 4, 'Avenida 68 #23-10', 'Cali', 'Valle del Cauca', '760001', 1),
(4, 5, 'Calle 10 #5-20', 'Barranquilla', 'Atlántico', '080001', 1),
(5, 6, 'Diagonal 30 #15-40', 'Bucaramanga', 'Santander', '680001', 1),
(6, 2, 'Calle 200 #10-15, Apto 302', 'Bogotá', 'Cundinamarca', '110221', 0);

--
-- Disparadores `direcciones`
--
DELIMITER $$
CREATE TRIGGER `trg_direccion_principal_unica` BEFORE INSERT ON `direcciones` FOR EACH ROW BEGIN
  IF NEW.principal = 1 THEN
    UPDATE direcciones SET principal = 0 WHERE user_id = NEW.user_id;
  END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresas_envio`
--

CREATE TABLE `empresas_envio` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `pagina_web` varchar(150) DEFAULT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empresas_envio`
--

INSERT INTO `empresas_envio` (`id`, `nombre`, `telefono`, `email`, `pagina_web`, `estado`) VALUES
(1, 'Servientrega', '6017700200', 'contacto@servientrega.com', 'https://www.servientrega.com', 'activo'),
(2, 'Inter Rapidísimo', '018000091234', 'servicio@interrapidisimo.com', 'https://www.interrapidisimo.com', 'activo'),
(3, 'Coordinadora', '018000520022', 'servicio@coordinadora.com', 'https://www.coordinadora.com', 'activo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `envios`
--

CREATE TABLE `envios` (
  `id` int(11) NOT NULL,
  `factura_id` int(11) NOT NULL,
  `empresa_envio_id` int(11) NOT NULL,
  `direccion_id` int(11) NOT NULL,
  `numero_guia` varchar(50) DEFAULT NULL,
  `costo_envio` decimal(10,2) NOT NULL,
  `fecha_envio` date DEFAULT NULL,
  `fecha_entrega` date DEFAULT NULL,
  `estado` enum('pendiente','en_transito','entregado','cancelado') DEFAULT 'pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `envios`
--

INSERT INTO `envios` (`id`, `factura_id`, `empresa_envio_id`, `direccion_id`, `numero_guia`, `costo_envio`, `fecha_envio`, `fecha_entrega`, `estado`) VALUES
(1, 1, 1, 1, 'SE123456789', 12000.00, '2026-07-15', '2026-07-17', 'entregado'),
(2, 2, 2, 3, 'IR987654321', 15000.00, '2026-07-16', NULL, 'en_transito'),
(3, 3, 3, 5, NULL, 10000.00, NULL, NULL, 'entregado'),
(4, 58, 2, 5, 'GUIA000582', 13500.00, '2026-06-28', NULL, 'en_transito'),
(5, 59, 2, 2, 'GUIA000592', 15000.00, '2026-06-28', NULL, 'en_transito'),
(6, 60, 3, 1, NULL, 18000.00, NULL, NULL, 'pendiente'),
(7, 61, 3, 3, 'GUIA000613', 10000.00, '2026-06-28', NULL, 'en_transito'),
(8, 62, 1, 3, NULL, 15000.00, NULL, NULL, 'cancelado'),
(9, 63, 1, 2, 'GUIA000631', 10000.00, '2026-06-29', '2026-07-02', 'entregado'),
(10, 64, 1, 4, 'GUIA000641', 10000.00, '2026-06-29', '2026-07-02', 'entregado'),
(11, 65, 3, 5, 'GUIA000653', 18000.00, '2026-06-29', '2026-06-30', 'entregado'),
(12, 66, 2, 5, 'GUIA000662', 18000.00, '2026-06-29', '2026-07-01', 'entregado'),
(13, 67, 1, 1, 'GUIA000671', 12000.00, '2026-06-30', '2026-07-01', 'entregado'),
(14, 68, 1, 2, NULL, 10000.00, NULL, NULL, 'pendiente'),
(15, 69, 1, 3, 'GUIA000691', 10000.00, '2026-06-30', '2026-07-02', 'entregado'),
(16, 70, 1, 2, 'GUIA000701', 13500.00, '2026-07-01', NULL, 'en_transito'),
(17, 71, 1, 5, 'GUIA000711', 13500.00, '2026-07-01', '2026-07-02', 'entregado'),
(18, 72, 1, 3, 'GUIA000721', 12000.00, '2026-07-02', NULL, 'en_transito'),
(19, 73, 1, 1, 'GUIA000731', 10000.00, '2026-07-02', '2026-07-04', 'entregado'),
(20, 74, 3, 4, 'GUIA000743', 13500.00, '2026-07-02', '2026-07-05', 'entregado'),
(21, 75, 2, 2, 'GUIA000752', 15000.00, '2026-07-03', '2026-07-04', 'entregado'),
(22, 76, 3, 2, NULL, 18000.00, NULL, NULL, 'pendiente'),
(23, 77, 2, 2, NULL, 12000.00, NULL, NULL, 'pendiente'),
(24, 78, 2, 1, 'GUIA000782', 13500.00, '2026-07-05', NULL, 'en_transito'),
(25, 79, 1, 3, 'GUIA000791', 12000.00, '2026-07-06', '2026-07-09', 'entregado'),
(26, 80, 2, 1, 'GUIA000802', 18000.00, '2026-07-07', NULL, 'en_transito'),
(27, 81, 3, 4, NULL, 15000.00, NULL, NULL, 'pendiente'),
(28, 82, 2, 5, 'GUIA000822', 12000.00, '2026-07-08', '2026-07-11', 'entregado'),
(29, 83, 2, 2, 'GUIA000832', 15000.00, '2026-07-10', '2026-07-13', 'entregado'),
(30, 84, 2, 4, 'GUIA000842', 10000.00, '2026-07-11', NULL, 'en_transito'),
(31, 85, 2, 4, 'GUIA000852', 13500.00, '2026-07-12', '2026-07-13', 'entregado'),
(32, 86, 1, 4, 'GUIA000861', 13500.00, '2026-07-14', '2026-07-17', 'entregado'),
(33, 87, 1, 3, 'GUIA000871', 18000.00, '2026-07-14', '2026-07-15', 'entregado'),
(34, 88, 1, 5, 'GUIA000881', 10000.00, '2026-07-15', '2026-07-16', 'entregado'),
(35, 89, 2, 3, 'GUIA000892', 12000.00, '2026-07-15', '2026-07-16', 'entregado'),
(36, 90, 3, 1, 'GUIA000903', 12000.00, '2026-07-16', NULL, 'en_transito'),
(37, 91, 2, 1, 'GUIA000912', 12000.00, '2026-07-16', '2026-07-19', 'entregado'),
(38, 92, 3, 4, 'GUIA000923', 10000.00, '2026-07-16', NULL, 'en_transito'),
(39, 93, 1, 1, NULL, 15000.00, NULL, NULL, 'cancelado'),
(40, 94, 1, 2, 'GUIA000941', 13500.00, '2026-07-20', '2026-07-21', 'entregado'),
(41, 95, 1, 4, 'GUIA000951', 13500.00, '2026-07-22', '2026-07-25', 'entregado'),
(42, 96, 2, 3, NULL, 18000.00, NULL, NULL, 'pendiente'),
(43, 97, 1, 2, NULL, 18000.00, NULL, NULL, 'pendiente'),
(44, 98, 1, 1, 'GUIA000981', 13500.00, '2026-07-23', '2026-07-25', 'entregado'),
(45, 99, 3, 5, NULL, 10000.00, NULL, NULL, 'pendiente'),
(46, 100, 2, 1, 'GUIA001002', 10000.00, '2026-07-23', '2026-07-24', 'entregado'),
(47, 101, 1, 4, 'GUIA001011', 13500.00, '2026-07-24', NULL, 'en_transito'),
(48, 102, 2, 5, 'GUIA001022', 10000.00, '2026-07-24', '2026-07-26', 'entregado'),
(49, 103, 2, 1, NULL, 18000.00, NULL, NULL, 'cancelado'),
(50, 104, 1, 4, NULL, 15000.00, NULL, NULL, 'pendiente'),
(51, 105, 3, 4, NULL, 12000.00, NULL, NULL, 'pendiente'),
(52, 106, 2, 3, 'GUIA001062', 15000.00, '2026-07-24', NULL, 'en_transito'),
(53, 107, 3, 3, 'GUIA001073', 10000.00, '2026-07-24', '2026-07-26', 'entregado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `existencias`
--

CREATE TABLE `existencias` (
  `id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `talla_id` int(11) NOT NULL,
  `color_id` int(11) NOT NULL,
  `sku` varchar(40) DEFAULT NULL,
  `precio` decimal(10,2) NOT NULL,
  `stock` int(11) NOT NULL DEFAULT 0,
  `estado` enum('activo','agotado') DEFAULT 'activo',
  `fecha_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `existencias`
--

INSERT INTO `existencias` (`id`, `producto_id`, `talla_id`, `color_id`, `sku`, `precio`, `stock`, `estado`, `fecha_actualizacion`) VALUES
(1, 1, 2, 1, 'REF001-S-NEG', 85000.00, 10, 'activo', '2026-07-20 20:39:50'),
(2, 1, 3, 1, 'REF001-M-NEG', 85000.00, 8, 'activo', '2026-07-20 20:39:50'),
(3, 1, 4, 1, 'REF001-L-NEG', 85000.00, 6, 'activo', '2026-07-20 20:39:50'),
(4, 1, 3, 2, 'REF001-M-BLA', 85000.00, 5, 'activo', '2026-07-20 20:39:50'),
(5, 1, 5, 3, 'REF001-XL-AZU', 90000.00, 50, 'activo', '2026-07-24 18:43:21'),
(6, 2, 2, 1, 'REF002-S-NEG', 65000.00, 12, 'activo', '2026-07-20 20:39:50'),
(7, 2, 3, 2, 'REF002-M-BLA', 65000.00, 15, 'activo', '2026-07-20 20:39:50'),
(8, 2, 4, 4, 'REF002-L-ROJ', 65000.00, 7, 'activo', '2026-07-20 20:39:50'),
(9, 3, 3, 1, 'REF003-M-NEG', 120000.00, 9, 'activo', '2026-07-20 20:39:50'),
(10, 3, 4, 3, 'REF003-L-AZU', 120000.00, 4, 'activo', '2026-07-20 20:39:50'),
(11, 4, 3, 1, 'REF004-M-NEG', 135000.00, 6, 'activo', '2026-07-20 20:39:50'),
(12, 4, 4, 1, 'REF004-L-NEG', 135000.00, 5, 'activo', '2026-07-20 20:39:50'),
(13, 5, 3, 1, 'REF005-M-NEG', 110000.00, 10, 'activo', '2026-07-20 20:39:50'),
(14, 5, 4, 2, 'REF005-L-BLA', 110000.00, 8, 'activo', '2026-07-20 20:39:50'),
(15, 6, 3, 3, 'REF006-M-AZU', 105000.00, 6, 'activo', '2026-07-20 20:39:50'),
(16, 6, 5, 1, 'REF006-XL-NEG', 105000.00, 3, 'activo', '2026-07-20 20:39:50'),
(17, 7, 3, 1, 'REF007-M-NEG', 180000.00, 5, 'activo', '2026-07-20 20:39:50'),
(18, 7, 4, 1, 'REF007-L-NEG', 180000.00, 4, 'activo', '2026-07-20 20:39:50'),
(19, 8, 3, 3, 'REF008-M-AZU', 175000.00, 6, 'activo', '2026-07-20 20:39:50'),
(20, 8, 4, 3, 'REF008-L-AZU', 175000.00, 3, 'activo', '2026-07-20 20:39:50'),
(21, 9, 2, 2, 'REF009-S-BLA', 70000.00, 10, 'activo', '2026-07-20 20:39:50'),
(22, 9, 3, 4, 'REF009-M-ROJ', 70000.00, 8, 'activo', '2026-07-20 20:39:50');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `facturas`
--

CREATE TABLE `facturas` (
  `id` int(11) NOT NULL,
  `numero_factura` varchar(20) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `direccion_id` int(11) NOT NULL,
  `metodo_pago_id` int(11) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `subtotal` decimal(10,2) NOT NULL,
  `iva` decimal(10,2) NOT NULL,
  `envio` decimal(10,2) NOT NULL,
  `total` decimal(10,2) NOT NULL,
  `estado` enum('activa','anulada') DEFAULT 'activa'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `facturas`
--

INSERT INTO `facturas` (`id`, `numero_factura`, `user_id`, `direccion_id`, `metodo_pago_id`, `fecha`, `subtotal`, `iva`, `envio`, `total`, `estado`) VALUES
(1, 'FAC-0001', 2, 1, 2, '2026-07-15 09:20:00', 290000.00, 55100.00, 12000.00, 357100.00, 'activa'),
(2, 'FAC-0002', 4, 3, 3, '2026-07-16 14:05:00', 310000.00, 58900.00, 15000.00, 383900.00, 'anulada'),
(3, 'FAC-0003', 6, 5, 4, '2026-07-19 11:30:00', 140000.00, 26600.00, 10000.00, 176600.00, 'activa'),
(4, 'FAC-0004', 3, 1, 2, '2026-07-24 12:39:58', 294117.65, 55882.35, 12000.00, 350000.00, 'anulada'),
(6, 'FAC-0005', 3, 1, 2, '2026-07-24 13:40:46', 294117.65, 55882.35, 12000.00, 350000.00, 'activa'),
(7, 'FAC-0007', 5, 4, 3, '2026-06-04 05:25:57', 360000.00, 68400.00, 10000.00, 438400.00, 'activa'),
(8, 'FAC-0006', 3, 1, 2, '2026-07-24 13:41:27', 294117.65, 55882.35, 12000.00, 350000.00, 'activa'),
(9, 'FAC-0009', 2, 1, 3, '2026-06-05 13:14:48', 675000.00, 128250.00, 13500.00, 816750.00, 'activa'),
(10, 'FAC-0010', 3, 2, 5, '2026-06-05 18:46:42', 350000.00, 66500.00, 15000.00, 431500.00, 'anulada'),
(11, 'FAC-0011', 2, 1, 3, '2026-06-08 02:04:30', 675000.00, 128250.00, 15000.00, 818250.00, 'activa'),
(12, 'FAC-0012', 3, 2, 6, '2026-06-08 23:37:03', 1330000.00, 252700.00, 12000.00, 1594700.00, 'activa'),
(13, 'FAC-0013', 6, 5, 4, '2026-06-09 01:55:43', 65000.00, 12350.00, 10000.00, 87350.00, 'activa'),
(14, 'FAC-0014', 2, 1, 1, '2026-06-09 18:34:55', 65000.00, 12350.00, 10000.00, 87350.00, 'activa'),
(15, 'FAC-0015', 3, 2, 5, '2026-06-10 08:06:48', 385000.00, 73150.00, 15000.00, 473150.00, 'activa'),
(16, 'FAC-0016', 5, 4, 4, '2026-06-10 10:19:32', 210000.00, 39900.00, 10000.00, 259900.00, 'activa'),
(17, 'FAC-0017', 3, 2, 2, '2026-06-10 17:21:55', 390000.00, 74100.00, 12000.00, 476100.00, 'activa'),
(18, 'FAC-0018', 2, 1, 4, '2026-06-11 06:10:01', 255000.00, 48450.00, 18000.00, 321450.00, 'anulada'),
(19, 'FAC-0019', 2, 1, 2, '2026-06-11 06:49:51', 325000.00, 61750.00, 15000.00, 401750.00, 'activa'),
(20, 'FAC-0020', 4, 3, 4, '2026-06-12 03:25:12', 760000.00, 144400.00, 12000.00, 916400.00, 'activa'),
(21, 'FAC-0021', 2, 1, 6, '2026-06-13 10:51:57', 885000.00, 168150.00, 10000.00, 1063150.00, 'activa'),
(22, 'FAC-0022', 3, 2, 4, '2026-06-14 21:08:48', 175000.00, 33250.00, 18000.00, 226250.00, 'activa'),
(23, 'FAC-0023', 6, 5, 5, '2026-06-16 10:17:36', 560000.00, 106400.00, 13500.00, 679900.00, 'activa'),
(24, 'FAC-0024', 2, 1, 1, '2026-06-16 20:01:59', 1125000.00, 213750.00, 12000.00, 1350750.00, 'activa'),
(25, 'FAC-0025', 4, 3, 3, '2026-06-20 00:03:53', 675000.00, 128250.00, 18000.00, 821250.00, 'activa'),
(26, 'FAC-0026', 4, 3, 6, '2026-06-20 15:19:31', 180000.00, 34200.00, 10000.00, 224200.00, 'activa'),
(27, 'FAC-0027', 6, 5, 2, '2026-06-22 05:43:02', 480000.00, 91200.00, 13500.00, 584700.00, 'activa'),
(28, 'FAC-0028', 2, 1, 3, '2026-06-22 13:27:48', 430000.00, 81700.00, 15000.00, 526700.00, 'anulada'),
(29, 'FAC-00029', 4, 3, 4, '2026-06-01 23:08:35', 660000.00, 125400.00, 10000.00, 795400.00, 'activa'),
(30, 'FAC-0030', 3, 2, 4, '2026-06-03 18:16:45', 745000.00, 141550.00, 10000.00, 896550.00, 'activa'),
(31, 'FAC-0031', 4, 3, 2, '2026-06-03 21:49:59', 665000.00, 126350.00, 18000.00, 809350.00, 'activa'),
(32, 'FAC-0032', 6, 5, 1, '2026-06-04 10:03:32', 1390000.00, 264100.00, 10000.00, 1664100.00, 'activa'),
(33, 'FAC-0033', 3, 2, 2, '2026-06-25 02:38:21', 70000.00, 13300.00, 15000.00, 98300.00, 'activa'),
(34, 'FAC-0034', 4, 3, 3, '2026-06-27 00:22:41', 820000.00, 155800.00, 13500.00, 989300.00, 'activa'),
(35, 'FAC-0035', 5, 4, 5, '2026-06-28 00:51:53', 330000.00, 62700.00, 12000.00, 404700.00, 'activa'),
(36, 'FAC-0036', 3, 2, 3, '2026-06-28 07:29:13', 1040000.00, 197600.00, 13500.00, 1251100.00, 'activa'),
(37, 'FAC-0037', 6, 5, 2, '2026-06-28 08:13:52', 430000.00, 81700.00, 12000.00, 523700.00, 'activa'),
(38, 'FAC-0038', 4, 3, 3, '2026-06-29 10:19:22', 855000.00, 162450.00, 13500.00, 1030950.00, 'activa'),
(39, 'FAC-0039', 3, 2, 6, '2026-06-29 19:09:17', 360000.00, 68400.00, 18000.00, 446400.00, 'activa'),
(40, 'FAC-0040', 3, 2, 2, '2026-07-04 00:19:19', 85000.00, 16150.00, 15000.00, 116150.00, 'activa'),
(41, 'FAC-0041', 6, 5, 2, '2026-07-04 08:50:28', 800000.00, 152000.00, 15000.00, 967000.00, 'activa'),
(42, 'FAC-0042', 6, 5, 2, '2026-07-04 17:28:29', 105000.00, 19950.00, 15000.00, 139950.00, 'activa'),
(43, 'FAC-0043', 5, 4, 5, '2026-07-06 04:28:57', 950000.00, 180500.00, 13500.00, 1144000.00, 'activa'),
(44, 'FAC-0044', 2, 1, 6, '2026-07-06 10:40:14', 625000.00, 118750.00, 12000.00, 755750.00, 'activa'),
(45, 'FAC-0045', 2, 1, 4, '2026-07-08 02:02:56', 745000.00, 141550.00, 18000.00, 904550.00, 'activa'),
(46, 'FAC-0046', 4, 3, 3, '2026-07-08 05:17:41', 880000.00, 167200.00, 15000.00, 1062200.00, 'activa'),
(47, 'FAC-0047', 3, 2, 4, '2026-07-12 01:33:07', 535000.00, 101650.00, 18000.00, 654650.00, 'activa'),
(48, 'FAC-0048', 3, 2, 4, '2026-07-12 07:08:56', 410000.00, 77900.00, 12000.00, 499900.00, 'activa'),
(49, 'FAC-0049', 4, 3, 1, '2026-07-12 08:45:46', 1115000.00, 211850.00, 10000.00, 1336850.00, 'activa'),
(50, 'FAC-0050', 6, 5, 2, '2026-07-14 22:43:58', 375000.00, 71250.00, 18000.00, 464250.00, 'activa'),
(51, 'FAC-0051', 3, 2, 5, '2026-07-15 22:32:15', 130000.00, 24700.00, 10000.00, 164700.00, 'activa'),
(52, 'FAC-0052', 5, 4, 6, '2026-07-20 09:33:47', 780000.00, 148200.00, 12000.00, 940200.00, 'activa'),
(53, 'FAC-0053', 2, 1, 5, '2026-07-23 09:30:07', 405000.00, 76950.00, 15000.00, 496950.00, 'activa'),
(54, 'FAC-0054', 5, 4, 5, '2026-06-22 17:39:49', 85000.00, 16150.00, 12000.00, 113150.00, 'activa'),
(55, 'FAC-0055', 5, 4, 2, '2026-06-23 00:07:07', 240000.00, 45600.00, 10000.00, 295600.00, 'activa'),
(56, 'FAC-0056', 6, 5, 4, '2026-06-23 11:02:29', 195000.00, 37050.00, 10000.00, 242050.00, 'activa'),
(57, 'FAC-0057', 3, 2, 3, '2026-06-23 22:08:21', 305000.00, 57950.00, 12000.00, 374950.00, 'activa'),
(58, 'FAC-0058', 6, 5, 1, '2026-06-27 03:41:08', 455000.00, 86450.00, 13500.00, 554950.00, 'activa'),
(59, 'FAC-0059', 3, 2, 2, '2026-06-27 14:16:21', 695000.00, 132050.00, 15000.00, 842050.00, 'activa'),
(60, 'FAC-0060', 2, 1, 5, '2026-06-27 16:15:27', 640000.00, 121600.00, 18000.00, 779600.00, 'activa'),
(61, 'FAC-0061', 4, 3, 5, '2026-06-27 17:46:32', 1040000.00, 197600.00, 10000.00, 1247600.00, 'activa'),
(62, 'FAC-0062', 4, 3, 6, '2026-06-28 03:34:25', 635000.00, 120650.00, 15000.00, 770650.00, 'anulada'),
(63, 'FAC-0063', 3, 2, 3, '2026-06-28 04:52:07', 350000.00, 66500.00, 10000.00, 426500.00, 'activa'),
(64, 'FAC-0064', 5, 4, 5, '2026-06-28 08:04:28', 425000.00, 80750.00, 10000.00, 515750.00, 'activa'),
(65, 'FAC-0065', 6, 5, 2, '2026-06-28 17:23:14', 675000.00, 128250.00, 18000.00, 821250.00, 'activa'),
(66, 'FAC-0066', 6, 5, 6, '2026-06-28 20:23:39', 315000.00, 59850.00, 18000.00, 392850.00, 'activa'),
(67, 'FAC-0067', 2, 1, 2, '2026-06-29 12:08:08', 130000.00, 24700.00, 12000.00, 166700.00, 'activa'),
(68, 'FAC-0068', 3, 2, 5, '2026-06-29 17:41:17', 405000.00, 76950.00, 10000.00, 491950.00, 'activa'),
(69, 'FAC-0069', 4, 3, 3, '2026-06-29 21:40:10', 590000.00, 112100.00, 10000.00, 712100.00, 'activa'),
(70, 'FAC-0070', 3, 2, 5, '2026-06-30 01:30:53', 195000.00, 37050.00, 13500.00, 245550.00, 'activa'),
(71, 'FAC-0071', 6, 5, 3, '2026-06-30 08:04:06', 360000.00, 68400.00, 13500.00, 441900.00, 'activa'),
(72, 'FAC-0072', 4, 3, 6, '2026-07-01 01:14:16', 305000.00, 57950.00, 12000.00, 374950.00, 'activa'),
(73, 'FAC-0073', 2, 1, 3, '2026-07-01 08:14:23', 1055000.00, 200450.00, 10000.00, 1265450.00, 'activa'),
(74, 'FAC-0074', 5, 4, 5, '2026-07-01 19:09:35', 315000.00, 59850.00, 13500.00, 388350.00, 'activa'),
(75, 'FAC-0075', 3, 2, 4, '2026-07-02 08:04:09', 290000.00, 55100.00, 15000.00, 360100.00, 'activa'),
(76, 'FAC-0076', 3, 2, 1, '2026-07-02 15:45:07', 630000.00, 119700.00, 18000.00, 767700.00, 'activa'),
(77, 'FAC-0077', 3, 2, 5, '2026-07-04 02:33:41', 295000.00, 56050.00, 12000.00, 363050.00, 'activa'),
(78, 'FAC-0078', 2, 1, 3, '2026-07-04 10:53:08', 660000.00, 125400.00, 13500.00, 798900.00, 'activa'),
(79, 'FAC-0079', 4, 3, 4, '2026-07-05 18:08:29', 1075000.00, 204250.00, 12000.00, 1291250.00, 'activa'),
(80, 'FAC-0080', 2, 1, 3, '2026-07-06 01:34:44', 595000.00, 113050.00, 18000.00, 726050.00, 'activa'),
(81, 'FAC-0081', 5, 4, 3, '2026-07-06 04:05:32', 675000.00, 128250.00, 15000.00, 818250.00, 'activa'),
(82, 'FAC-0082', 6, 5, 2, '2026-07-07 00:23:33', 815000.00, 154850.00, 12000.00, 981850.00, 'activa'),
(83, 'FAC-0083', 3, 2, 6, '2026-07-09 09:25:09', 555000.00, 105450.00, 15000.00, 675450.00, 'activa'),
(84, 'FAC-0084', 5, 4, 5, '2026-07-10 07:24:26', 845000.00, 160550.00, 10000.00, 1015550.00, 'activa'),
(85, 'FAC-0085', 5, 4, 3, '2026-07-11 01:17:33', 350000.00, 66500.00, 13500.00, 430000.00, 'activa'),
(86, 'FAC-0086', 5, 4, 6, '2026-07-13 02:03:30', 960000.00, 182400.00, 13500.00, 1155900.00, 'activa'),
(87, 'FAC-0087', 4, 3, 1, '2026-07-13 09:52:28', 120000.00, 22800.00, 18000.00, 160800.00, 'activa'),
(88, 'FAC-0088', 6, 5, 4, '2026-07-14 12:00:09', 880000.00, 167200.00, 10000.00, 1057200.00, 'activa'),
(89, 'FAC-0089', 4, 3, 5, '2026-07-14 14:09:58', 675000.00, 128250.00, 12000.00, 815250.00, 'activa'),
(90, 'FAC-0090', 2, 1, 1, '2026-07-15 15:12:21', 540000.00, 102600.00, 12000.00, 654600.00, 'activa'),
(91, 'FAC-0091', 2, 1, 6, '2026-07-15 16:19:56', 1070000.00, 203300.00, 12000.00, 1285300.00, 'activa'),
(92, 'FAC-0092', 5, 4, 3, '2026-07-15 22:36:02', 90000.00, 17100.00, 10000.00, 117100.00, 'activa'),
(93, 'FAC-0093', 2, 1, 1, '2026-07-16 09:14:01', 805000.00, 152950.00, 15000.00, 972950.00, 'anulada'),
(94, 'FAC-0094', 3, 2, 3, '2026-07-19 23:12:19', 765000.00, 145350.00, 13500.00, 923850.00, 'activa'),
(95, 'FAC-0095', 5, 4, 3, '2026-07-21 08:20:52', 245000.00, 46550.00, 13500.00, 305050.00, 'activa'),
(96, 'FAC-0096', 4, 3, 3, '2026-07-21 13:56:40', 430000.00, 81700.00, 18000.00, 529700.00, 'activa'),
(97, 'FAC-0097', 3, 2, 3, '2026-07-22 02:00:59', 615000.00, 116850.00, 18000.00, 749850.00, 'activa'),
(98, 'FAC-0098', 2, 1, 6, '2026-07-22 08:33:41', 170000.00, 32300.00, 13500.00, 215800.00, 'activa'),
(99, 'FAC-0099', 6, 5, 6, '2026-07-22 12:44:49', 345000.00, 65550.00, 10000.00, 420550.00, 'activa'),
(100, 'FAC-0100', 2, 1, 6, '2026-07-22 18:48:04', 210000.00, 39900.00, 10000.00, 259900.00, 'activa'),
(101, 'FAC-0101', 5, 4, 4, '2026-07-23 01:09:45', 315000.00, 59850.00, 13500.00, 388350.00, 'activa'),
(102, 'FAC-0102', 6, 5, 2, '2026-07-23 01:30:04', 690000.00, 131100.00, 10000.00, 831100.00, 'activa'),
(103, 'FAC-0103', 2, 1, 6, '2026-07-23 08:22:25', 455000.00, 86450.00, 18000.00, 559450.00, 'anulada'),
(104, 'FAC-0104', 5, 4, 4, '2026-07-23 13:36:47', 750000.00, 142500.00, 15000.00, 907500.00, 'activa'),
(105, 'FAC-0105', 5, 4, 3, '2026-07-23 14:59:50', 980000.00, 186200.00, 12000.00, 1178200.00, 'activa'),
(106, 'FAC-0106', 4, 3, 2, '2026-07-23 15:14:26', 710000.00, 134900.00, 15000.00, 859900.00, 'activa'),
(107, 'FAC-0107', 4, 3, 1, '2026-07-23 18:12:18', 550000.00, 104500.00, 10000.00, 664500.00, 'activa');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `imagenes_producto`
--

CREATE TABLE `imagenes_producto` (
  `id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `imagen` varchar(255) NOT NULL,
  `principal` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `imagenes_producto`
--

INSERT INTO `imagenes_producto` (`id`, `producto_id`, `imagen`, `principal`) VALUES
(1, 1, 'camiseta_oversize.jpg', 1),
(2, 2, 'camiseta_basica.jpg', 1),
(3, 3, 'pantalon_jogger.jpg', 1),
(4, 4, 'pantalon_cargo.jpg', 1),
(5, 5, 'sudadera_hoodie.jpg', 1),
(6, 6, 'sudadera_crewneck.jpg', 1),
(7, 7, 'chaqueta_bomber.jpg', 1),
(8, 8, 'chaqueta_denim.jpg', 1),
(9, 9, 'camiseta_estampada.jpg', 1),
(10, 10, 'camiseta.jpg', 1);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `marcas`
--

CREATE TABLE `marcas` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `marcas`
--

INSERT INTO `marcas` (`id`, `nombre`) VALUES
(3, 'Adidas'),
(2, 'Nike'),
(4, 'Puma'),
(1, 'UrbanStyle');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `metodos_pago`
--

CREATE TABLE `metodos_pago` (
  `id` int(11) NOT NULL,
  `nombre` varchar(60) NOT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `metodos_pago`
--

INSERT INTO `metodos_pago` (`id`, `nombre`, `estado`) VALUES
(1, 'Tarjeta Crédito', 'activo'),
(2, 'Tarjeta Débito', 'activo'),
(3, 'PSE', 'activo'),
(4, 'Nequi', 'activo'),
(5, 'Daviplata', 'activo'),
(6, 'Efectivo', 'activo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos`
--

CREATE TABLE `pagos` (
  `id` int(11) NOT NULL,
  `factura_id` int(11) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha_pago` datetime DEFAULT current_timestamp(),
  `estado` enum('pendiente','pagado') DEFAULT 'pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pagos`
--

INSERT INTO `pagos` (`id`, `factura_id`, `monto`, `fecha_pago`, `estado`) VALUES
(1, 1, 357100.00, '2026-07-15 09:22:00', 'pagado'),
(2, 2, 383900.00, '2026-07-16 14:07:00', 'pagado'),
(3, 3, 176600.00, '2026-07-19 11:31:00', 'pendiente'),
(4, 58, 554950.00, '2026-06-27 03:51:08', 'pagado'),
(5, 59, 842050.00, '2026-06-27 14:19:21', 'pagado'),
(6, 60, 779600.00, '2026-06-27 16:26:27', 'pagado'),
(7, 61, 1247600.00, '2026-06-27 18:01:32', 'pagado'),
(8, 62, 770650.00, '2026-06-28 03:34:25', 'pendiente'),
(9, 63, 426500.00, '2026-06-28 04:57:07', 'pagado'),
(10, 64, 515750.00, '2026-06-28 08:20:28', 'pagado'),
(11, 65, 821250.00, '2026-06-28 17:40:14', 'pagado'),
(12, 66, 392850.00, '2026-06-28 20:36:39', 'pagado'),
(13, 67, 166700.00, '2026-06-29 12:27:08', 'pagado'),
(14, 68, 491950.00, '2026-06-29 17:46:17', 'pagado'),
(15, 69, 712100.00, '2026-06-29 21:56:10', 'pagado'),
(16, 70, 245550.00, '2026-06-30 01:30:53', 'pendiente'),
(17, 71, 441900.00, '2026-06-30 08:21:06', 'pagado'),
(18, 72, 374950.00, '2026-07-01 01:15:16', 'pagado'),
(19, 73, 1265450.00, '2026-07-01 08:21:23', 'pagado'),
(20, 74, 388350.00, '2026-07-01 19:22:35', 'pagado'),
(21, 75, 360100.00, '2026-07-02 08:10:09', 'pagado'),
(22, 76, 767700.00, '2026-07-02 15:57:07', 'pagado'),
(23, 77, 363050.00, '2026-07-04 02:40:41', 'pagado'),
(24, 78, 798900.00, '2026-07-04 10:55:08', 'pagado'),
(25, 79, 1291250.00, '2026-07-05 18:26:29', 'pagado'),
(26, 80, 726050.00, '2026-07-06 01:37:44', 'pagado'),
(27, 81, 818250.00, '2026-07-06 04:14:32', 'pagado'),
(28, 82, 981850.00, '2026-07-07 00:27:33', 'pagado'),
(29, 83, 675450.00, '2026-07-09 09:31:09', 'pagado'),
(30, 84, 1015550.00, '2026-07-10 07:25:26', 'pagado'),
(31, 85, 430000.00, '2026-07-11 01:22:33', 'pagado'),
(32, 86, 1155900.00, '2026-07-13 02:06:30', 'pagado'),
(33, 87, 160800.00, '2026-07-13 10:03:28', 'pagado'),
(34, 88, 1057200.00, '2026-07-14 12:10:09', 'pagado'),
(35, 89, 815250.00, '2026-07-14 14:09:58', 'pendiente'),
(36, 90, 654600.00, '2026-07-15 15:12:21', 'pendiente'),
(37, 91, 1285300.00, '2026-07-15 16:24:56', 'pagado'),
(38, 92, 117100.00, '2026-07-15 22:42:02', 'pagado'),
(39, 93, 972950.00, '2026-07-16 09:14:01', 'pendiente'),
(40, 94, 923850.00, '2026-07-19 23:15:19', 'pagado'),
(41, 95, 305050.00, '2026-07-21 08:21:52', 'pagado'),
(42, 96, 529700.00, '2026-07-21 14:12:40', 'pagado'),
(43, 97, 749850.00, '2026-07-22 02:19:59', 'pagado'),
(44, 98, 215800.00, '2026-07-22 08:34:41', 'pagado'),
(45, 99, 420550.00, '2026-07-22 12:44:49', 'pendiente'),
(46, 100, 259900.00, '2026-07-22 19:03:04', 'pagado'),
(47, 101, 388350.00, '2026-07-23 01:12:45', 'pagado'),
(48, 102, 831100.00, '2026-07-23 01:30:04', 'pendiente'),
(49, 103, 559450.00, '2026-07-23 08:22:25', 'pendiente'),
(50, 104, 907500.00, '2026-07-23 13:36:47', 'pendiente'),
(51, 105, 1178200.00, '2026-07-23 15:03:50', 'pagado'),
(52, 106, 859900.00, '2026-07-23 15:27:26', 'pagado'),
(53, 107, 664500.00, '2026-07-23 18:25:18', 'pagado');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `referencia` varchar(30) DEFAULT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `categoria_id` int(11) NOT NULL,
  `marca_id` int(11) NOT NULL,
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id`, `referencia`, `nombre`, `descripcion`, `categoria_id`, `marca_id`, `estado`, `created_at`, `updated_at`) VALUES
(1, 'REF001', 'Camiseta Oversize', 'Nueva descripción', 1, 1, 'activo', '2026-07-20 23:41:44', '2026-07-24 18:43:21'),
(2, 'REF002', 'Camiseta Básica', 'Camiseta 100% algodón, corte clásico', 1, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(3, 'REF003', 'Pantalón Jogger', 'Jogger deportivo con puños ajustados', 2, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(4, 'REF004', 'Pantalón Cargo', 'Pantalón cargo con bolsillos laterales', 2, 2, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(5, 'REF005', 'Sudadera Hoodie', 'Sudadera con capota y bolsillo canguro', 3, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(6, 'REF006', 'Sudadera Crewneck', 'Sudadera cuello redondo unisex', 3, 3, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(7, 'REF007', 'Chaqueta Bomber', 'Chaqueta bomber con forro interno', 4, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(8, 'REF008', 'Chaqueta Denim', 'Chaqueta de jean clásica', 4, 2, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(9, 'REF009', 'Camiseta Estampada', 'Camiseta con estampado gráfico frontal', 1, 3, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(10, 'REF010', 'Camiseta Oversize', '100% algodón', 1, 1, 'activo', '2026-07-24 18:43:21', '2026-07-24 18:43:21');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tallas`
--

CREATE TABLE `tallas` (
  `id` int(11) NOT NULL,
  `nombre` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tallas`
--

INSERT INTO `tallas` (`id`, `nombre`) VALUES
(4, 'L'),
(3, 'M'),
(2, 'S'),
(5, 'XL'),
(1, 'XS');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `documento_identidad` varchar(20) DEFAULT NULL,
  `email` varchar(120) NOT NULL,
  `password` varchar(255) NOT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `fechanaci` date DEFAULT NULL,
  `rol` enum('admin','usuario') DEFAULT 'usuario',
  `estado` enum('activo','inactivo') DEFAULT 'activo',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `users`
--

INSERT INTO `users` (`id`, `username`, `name`, `apellidos`, `documento_identidad`, `email`, `password`, `celular`, `fechanaci`, `rol`, `estado`, `created_at`, `updated_at`) VALUES
(1, 'Lokiur', 'Lokiur', 'Admin', NULL, 'test@test.com', '1233', NULL, NULL, 'admin', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(2, 'jperez', 'Juan', 'Pérez', NULL, 'juan.perez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000001', '3001234567', '1995-03-14', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(3, 'mrodriguez', 'María', 'Rodríguez', NULL, 'maria.rodriguez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000002', '3009876543', '1998-07-22', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(4, 'clopez', 'Carlos', 'López', NULL, 'carlos.lopez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000003', '3112345678', '1992-11-05', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(5, 'agomez', 'Ana', 'Gómez', NULL, 'ana.gomez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000004', '3157654321', '2000-01-30', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(6, 'sfernandez', 'Sofía', 'Fernández', NULL, 'sofia.fernandez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000005', '3201112233', '1997-09-18', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(7, 'dmartinez', 'Diego', 'Martínez', NULL, 'diego.martinez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000006', '3223334455', '1994-05-27', 'usuario', 'inactivo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(8, 'juan01', 'Juan', 'Pérez', NULL, 'juan@gmail.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '3001234567', NULL, 'usuario', 'activo', '2026-07-24 17:38:33', '2026-07-24 17:38:33'),
(11, 'juan10', 'Juan', 'Pérez', NULL, 'juan_@gmail.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', '3001234567', NULL, 'usuario', 'activo', '2026-07-24 18:37:40', '2026-07-24 18:37:40');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `colores`
--
ALTER TABLE `colores`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `detalle_carrito`
--
ALTER TABLE `detalle_carrito`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_carrito_existencia` (`carrito_id`,`existencia_id`),
  ADD KEY `carrito_id` (`carrito_id`),
  ADD KEY `existencia_id` (`existencia_id`);

--
-- Indices de la tabla `detalle_factura`
--
ALTER TABLE `detalle_factura`
  ADD PRIMARY KEY (`id`),
  ADD KEY `factura_id` (`factura_id`),
  ADD KEY `existencia_id` (`existencia_id`);

--
-- Indices de la tabla `direcciones`
--
ALTER TABLE `direcciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indices de la tabla `empresas_envio`
--
ALTER TABLE `empresas_envio`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `envios`
--
ALTER TABLE `envios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_guia` (`numero_guia`),
  ADD KEY `factura_id` (`factura_id`),
  ADD KEY `empresa_envio_id` (`empresa_envio_id`),
  ADD KEY `direccion_id` (`direccion_id`);

--
-- Indices de la tabla `existencias`
--
ALTER TABLE `existencias`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_existencia` (`producto_id`,`talla_id`,`color_id`),
  ADD UNIQUE KEY `sku` (`sku`),
  ADD KEY `talla_id` (`talla_id`),
  ADD KEY `color_id` (`color_id`),
  ADD KEY `idx_estado` (`estado`);

--
-- Indices de la tabla `facturas`
--
ALTER TABLE `facturas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `numero_factura` (`numero_factura`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `direccion_id` (`direccion_id`),
  ADD KEY `metodo_pago_id` (`metodo_pago_id`);

--
-- Indices de la tabla `imagenes_producto`
--
ALTER TABLE `imagenes_producto`
  ADD PRIMARY KEY (`id`),
  ADD KEY `producto_id` (`producto_id`);

--
-- Indices de la tabla `marcas`
--
ALTER TABLE `marcas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `metodos_pago`
--
ALTER TABLE `metodos_pago`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `factura_id` (`factura_id`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `referencia` (`referencia`),
  ADD KEY `categoria_id` (`categoria_id`),
  ADD KEY `marca_id` (`marca_id`),
  ADD KEY `idx_estado` (`estado`);
ALTER TABLE `productos` ADD FULLTEXT KEY `ft_nombre_desc` (`nombre`,`descripcion`);

--
-- Indices de la tabla `tallas`
--
ALTER TABLE `tallas`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `users`
-- (estas UNIQUE KEY ya cubren lo que pedía migracion_v2.sql
-- con `uq_username`/`uq_email`, por eso no se repiten)
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `carrito`
--
ALTER TABLE `carrito`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `colores`
--
ALTER TABLE `colores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `detalle_carrito`
--
ALTER TABLE `detalle_carrito`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `detalle_factura`
--
ALTER TABLE `detalle_factura`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=188;

--
-- AUTO_INCREMENT de la tabla `direcciones`
--
ALTER TABLE `direcciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `empresas_envio`
--
ALTER TABLE `empresas_envio`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `envios`
--
ALTER TABLE `envios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `existencias`
--
ALTER TABLE `existencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT de la tabla `facturas`
--
ALTER TABLE `facturas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=108;

--
-- AUTO_INCREMENT de la tabla `imagenes_producto`
--
ALTER TABLE `imagenes_producto`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `marcas`
--
ALTER TABLE `marcas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `metodos_pago`
--
ALTER TABLE `metodos_pago`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `pagos`
--
ALTER TABLE `pagos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=54;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `tallas`
--
ALTER TABLE `tallas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `carrito`
--
ALTER TABLE `carrito`
  ADD CONSTRAINT `carrito_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Filtros para la tabla `detalle_carrito`
--
ALTER TABLE `detalle_carrito`
  ADD CONSTRAINT `detalle_carrito_ibfk_1` FOREIGN KEY (`carrito_id`) REFERENCES `carrito` (`id`),
  ADD CONSTRAINT `detalle_carrito_ibfk_2` FOREIGN KEY (`existencia_id`) REFERENCES `existencias` (`id`);

--
-- Filtros para la tabla `detalle_factura`
--
ALTER TABLE `detalle_factura`
  ADD CONSTRAINT `detalle_factura_ibfk_1` FOREIGN KEY (`factura_id`) REFERENCES `facturas` (`id`),
  ADD CONSTRAINT `detalle_factura_ibfk_2` FOREIGN KEY (`existencia_id`) REFERENCES `existencias` (`id`);

--
-- Filtros para la tabla `direcciones`
--
ALTER TABLE `direcciones`
  ADD CONSTRAINT `direcciones_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`);

--
-- Filtros para la tabla `envios`
--
ALTER TABLE `envios`
  ADD CONSTRAINT `envios_ibfk_1` FOREIGN KEY (`factura_id`) REFERENCES `facturas` (`id`),
  ADD CONSTRAINT `envios_ibfk_2` FOREIGN KEY (`empresa_envio_id`) REFERENCES `empresas_envio` (`id`),
  ADD CONSTRAINT `envios_ibfk_3` FOREIGN KEY (`direccion_id`) REFERENCES `direcciones` (`id`);

--
-- Filtros para la tabla `existencias`
--
ALTER TABLE `existencias`
  ADD CONSTRAINT `existencias_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`),
  ADD CONSTRAINT `existencias_ibfk_2` FOREIGN KEY (`talla_id`) REFERENCES `tallas` (`id`),
  ADD CONSTRAINT `existencias_ibfk_3` FOREIGN KEY (`color_id`) REFERENCES `colores` (`id`);

--
-- Filtros para la tabla `facturas`
--
ALTER TABLE `facturas`
  ADD CONSTRAINT `facturas_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `facturas_ibfk_2` FOREIGN KEY (`direccion_id`) REFERENCES `direcciones` (`id`),
  ADD CONSTRAINT `facturas_ibfk_3` FOREIGN KEY (`metodo_pago_id`) REFERENCES `metodos_pago` (`id`);

--
-- Filtros para la tabla `imagenes_producto`
--
ALTER TABLE `imagenes_producto`
  ADD CONSTRAINT `imagenes_producto_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`);

--
-- Filtros para la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD CONSTRAINT `pagos_ibfk_1` FOREIGN KEY (`factura_id`) REFERENCES `facturas` (`id`);

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`),
  ADD CONSTRAINT `productos_ibfk_2` FOREIGN KEY (`marca_id`) REFERENCES `marcas` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
