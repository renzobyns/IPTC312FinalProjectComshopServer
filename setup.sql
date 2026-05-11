-- Comshop Management System — Database Setup
-- Run this once in phpMyAdmin or: mysql -u root < setup.sql

CREATE DATABASE IF NOT EXISTS comshop_db;
USE comshop_db;

DROP TABLE IF EXISTS transaction_items;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS print_services;
DROP TABLE IF EXISTS time_packages;
DROP TABLE IF EXISTS pc_units;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pc_units (
    id INT AUTO_INCREMENT PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL,
    status ENUM('available','occupied','maintenance') DEFAULT 'available',
    rate_per_hour DECIMAL(8,2) NOT NULL DEFAULT 20.00
);

CREATE TABLE time_packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    package_name VARCHAR(100) NOT NULL,
    hours DECIMAL(4,1) NOT NULL,
    price DECIMAL(8,2) NOT NULL
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category ENUM('food','drink') NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
);

CREATE TABLE print_services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    price_per_page DECIMAL(8,2) NOT NULL
);

CREATE TABLE sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pc_id INT NOT NULL,
    customer_name VARCHAR(100) NOT NULL,
    billing_type ENUM('hourly','package') NOT NULL DEFAULT 'hourly',
    package_id INT NULL,
    preset_hours DECIMAL(5,2) NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,
    total_amount DECIMAL(8,2) NULL,
    -- Migration for existing DBs: ALTER TABLE sessions MODIFY status ENUM('active','completed','cancelled') DEFAULT 'active';
    status ENUM('active','completed','cancelled') DEFAULT 'active',
    FOREIGN KEY (pc_id) REFERENCES pc_units(id),
    FOREIGN KEY (package_id) REFERENCES time_packages(id)
);

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('pc_rental','food','printing') NOT NULL,
    reference_id INT NULL,
    customer_name VARCHAR(100) NOT NULL,
    total_amount DECIMAL(8,2) NOT NULL,
    datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_by INT NULL,
    FOREIGN KEY (processed_by) REFERENCES users(id)
);

CREATE TABLE transaction_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id INT NOT NULL,
    item_name VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(8,2) NOT NULL,
    subtotal DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (transaction_id) REFERENCES transactions(id)
);

-- Seed: Admin (password: admin123)
-- SHA-256 of "admin123" = 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
INSERT INTO users (username, password_hash, full_name) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrator');

-- Seed: PC Units
INSERT INTO pc_units (unit_name, status, rate_per_hour) VALUES
('PC-01', 'available', 20.00),
('PC-02', 'available', 20.00),
('PC-03', 'available', 20.00),
('PC-04', 'available', 20.00),
('PC-05', 'available', 20.00);

-- Seed: Time Packages
INSERT INTO time_packages (package_name, hours, price) VALUES
('1HR Promo', 1.0, 15.00),
('3HRS Deal', 3.0, 40.00),
('5HRS Value', 5.0, 60.00);

-- Seed: Products
INSERT INTO products (name, category, price, stock) VALUES
('Coke',   'drink', 20.00, 50),
('Water',  'drink', 10.00, 100),
('Coffee', 'drink', 25.00, 30),
('Chips',  'food',  15.00, 40),
('Bread',  'food',  10.00, 25);

-- Seed: Print Services
INSERT INTO print_services (service_name, price_per_page) VALUES
('B&W Print',     2.00),
('Colored Print', 5.00);
