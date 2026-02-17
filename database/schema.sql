CREATE DATABASE IF NOT EXISTS financeiro_db;
USE financeiro_db;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS transacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo ENUM('entrada', 'despesa') NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    data DATE NOT NULL,
    descricao VARCHAR(200),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);