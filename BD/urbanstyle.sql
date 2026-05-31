-- ===============================
-- BASE DE DATOS
-- ===============================
CREATE DATABASE IF NOT EXISTS urbanstyle;
USE urbanstyle;

-- ===============================
-- TABLA USERS (usuarios + admins)
-- ===============================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    celular VARCHAR(20),
    fechanaci DATE,
    rol ENUM('admin','usuario') NOT NULL DEFAULT 'usuario',
    estado ENUM('activo','inactivo') NOT NULL DEFAULT 'activo'
);

-- ===============================
-- DIRECCIONES DE USUARIO
-- ===============================
CREATE TABLE direcciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    direccion TEXT NOT NULL,
    ciudad VARCHAR(100),
    estado VARCHAR(100),
    codigo_postal VARCHAR(10),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- ===============================
-- CATEGORÍAS
-- ===============================
CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL
);

-- ===============================
-- PRODUCTOS
-- ===============================
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    talla VARCHAR(10),
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL,
    categoria_id INT,
    estado ENUM('activo','inactivo') DEFAULT 'activo',
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);

-- ===============================
-- MÉTODOS DE PAGO
-- ===============================
CREATE TABLE metodos_pago (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- ===============================
-- FACTURAS
-- ===============================
CREATE TABLE facturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    direccion_id INT NOT NULL,
    metodo_pago_id INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10,2) NOT NULL,
    iva DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    estado ENUM('activa','anulada') DEFAULT 'activa',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (direccion_id) REFERENCES direcciones(id),
    FOREIGN KEY (metodo_pago_id) REFERENCES metodos_pago(id)
);

-- ===============================
-- DETALLE FACTURA
-- ===============================
CREATE TABLE detalle_factura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (factura_id) REFERENCES facturas(id),
    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

-- ===============================
-- PAGOS
-- ===============================
CREATE TABLE pagos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    monto DECIMAL(10,2) NOT NULL,
    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pagado','no_pagado') DEFAULT 'pagado',
    FOREIGN KEY (factura_id) REFERENCES facturas(id)
);

-- ===============================
-- ENVÍOS
-- ===============================
CREATE TABLE envios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    direccion_id INT NOT NULL,
    costo_envio DECIMAL(10,2) NOT NULL,
    fecha_envio DATE,
    estado VARCHAR(50),
    FOREIGN KEY (factura_id) REFERENCES facturas(id),
    FOREIGN KEY (direccion_id) REFERENCES direcciones(id)
);

-- ===============================
-- DATOS INICIALES
-- ===============================

-- Usuario admin solicitado
INSERT INTO users
(username, name, apellidos, email, password, rol, estado)
VALUES
('Lokiur', 'Lokiur', 'Admin', 'test@test.com', '1233', 'admin', 'activo');

-- Categorías
INSERT INTO categorias (nombre) VALUES
('Camisetas'),
('Pantalones'),
('Sudaderas'),
('Chaquetas');

-- Métodos de pago
INSERT INTO metodos_pago (nombre) VALUES
('Tarjeta de crédito'),
('Tarjeta de débito'),
('Transferencia'),
('Efectivo');
