-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 21-07-2026 a las 02:26:10
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

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
(1, 1, 7, 2),
(2, 1, 13, 1),
(3, 2, 21, 3);

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
(5, 3, 21, 2, 70000.00, 140000.00);

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
(3, 3, 3, 5, NULL, 10000.00, NULL, NULL, 'pendiente');

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
) ;

--
-- Volcado de datos para la tabla `existencias`
--

INSERT INTO `existencias` (`id`, `producto_id`, `talla_id`, `color_id`, `sku`, `precio`, `stock`, `estado`, `fecha_actualizacion`) VALUES
(1, 1, 2, 1, 'REF001-S-NEG', 85000.00, 10, 'activo', '2026-07-20 20:39:50'),
(2, 1, 3, 1, 'REF001-M-NEG', 85000.00, 8, 'activo', '2026-07-20 20:39:50'),
(3, 1, 4, 1, 'REF001-L-NEG', 85000.00, 6, 'activo', '2026-07-20 20:39:50'),
(4, 1, 3, 2, 'REF001-M-BLA', 85000.00, 5, 'activo', '2026-07-20 20:39:50'),
(5, 1, 5, 3, 'REF001-XL-AZU', 90000.00, 3, 'activo', '2026-07-20 20:39:50'),
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
(1, 'FAC-0001', 2, 1, 1, '2026-07-15 09:20:00', 290000.00, 55100.00, 12000.00, 357100.00, 'activa'),
(2, 'FAC-0002', 4, 3, 3, '2026-07-16 14:05:00', 310000.00, 58900.00, 15000.00, 383900.00, 'activa'),
(3, 'FAC-0003', 6, 5, 4, '2026-07-19 11:30:00', 140000.00, 26600.00, 10000.00, 176600.00, 'activa');

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
(9, 9, 'camiseta_estampada.jpg', 1);

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
(3, 3, 176600.00, '2026-07-19 11:31:00', 'pendiente');

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
(1, 'REF001', 'Camiseta Oversize', 'Camiseta algodón premium', 1, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(2, 'REF002', 'Camiseta Básica', 'Camiseta 100% algodón, corte clásico', 1, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(3, 'REF003', 'Pantalón Jogger', 'Jogger deportivo con puños ajustados', 2, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(4, 'REF004', 'Pantalón Cargo', 'Pantalón cargo con bolsillos laterales', 2, 2, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(5, 'REF005', 'Sudadera Hoodie', 'Sudadera con capota y bolsillo canguro', 3, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(6, 'REF006', 'Sudadera Crewneck', 'Sudadera cuello redondo unisex', 3, 3, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(7, 'REF007', 'Chaqueta Bomber', 'Chaqueta bomber con forro interno', 4, 1, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(8, 'REF008', 'Chaqueta Denim', 'Chaqueta de jean clásica', 4, 2, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(9, 'REF009', 'Camiseta Estampada', 'Camiseta con estampado gráfico frontal', 1, 3, 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44');

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

INSERT INTO `users` (`id`, `username`, `name`, `apellidos`, `email`, `password`, `celular`, `fechanaci`, `rol`, `estado`, `created_at`, `updated_at`) VALUES
(1, 'Lokiur', 'Lokiur', 'Admin', 'test@test.com', '1233', NULL, NULL, 'admin', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(2, 'jperez', 'Juan', 'Pérez', 'juan.perez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000001', '3001234567', '1995-03-14', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(3, 'mrodriguez', 'María', 'Rodríguez', 'maria.rodriguez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000002', '3009876543', '1998-07-22', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(4, 'clopez', 'Carlos', 'López', 'carlos.lopez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000003', '3112345678', '1992-11-05', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(5, 'agomez', 'Ana', 'Gómez', 'ana.gomez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000004', '3157654321', '2000-01-30', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(6, 'sfernandez', 'Sofía', 'Fernández', 'sofia.fernandez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000005', '3201112233', '1997-09-18', 'usuario', 'activo', '2026-07-20 23:41:44', '2026-07-20 23:41:44'),
(7, 'dmartinez', 'Diego', 'Martínez', 'diego.martinez@example.com', '$2y$10$examplehash0000000000000000000000000000000000000006', '3223334455', '1994-05-27', 'usuario', 'inactivo', '2026-07-20 23:41:44', '2026-07-20 23:41:44');

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `colores`
--
ALTER TABLE `colores`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `detalle_carrito`
--
ALTER TABLE `detalle_carrito`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `detalle_factura`
--
ALTER TABLE `detalle_factura`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `existencias`
--
ALTER TABLE `existencias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `facturas`
--
ALTER TABLE `facturas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `imagenes_producto`
--
ALTER TABLE `imagenes_producto`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `tallas`
--
ALTER TABLE `tallas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

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
