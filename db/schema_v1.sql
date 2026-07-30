-- ============================================
-- 液压支架智能体数据库 Schema v1
-- ============================================
USE hydraulic_support;

-- 先禁用外键检查，确保能顺利删除旧表
SET FOREIGN_KEY_CHECKS = 0;

-- 按正确顺序删除旧表（先子后父）
DROP TABLE IF EXISTS stent_parts;
DROP TABLE IF EXISTS working_conditions;
DROP TABLE IF EXISTS support_models;
DROP TABLE IF EXISTS mining_areas;
DROP TABLE IF EXISTS param_dependencies;

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- 1. 矿区表（无外部依赖，最先创建）
CREATE TABLE IF NOT EXISTS mining_areas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    area_name VARCHAR(50) NOT NULL,
    mine_name VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. 支架型号表（无外部依赖）
CREATE TABLE IF NOT EXISTS support_models (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model VARCHAR(50) NOT NULL UNIQUE,
    type VARCHAR(20),
    working_resistance INT,
    height_min DECIMAL(5,2),
    height_max DECIMAL(5,2),
    manufacturer VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 工况表（依赖 mining_areas 和 support_models）
CREATE TABLE IF NOT EXISTS working_conditions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    area_id INT NOT NULL,
    support_model_id INT,
    working_face_name VARCHAR(50),
    coal_thickness DECIMAL(5,2),
    roof_condition VARCHAR(20),
    floor_condition VARCHAR(20),
    dip_angle DECIMAL(4,1),
    gas_level VARCHAR(20),
    mining_height DECIMAL(5,2),
    daily_output INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (area_id) REFERENCES mining_areas(id) ON DELETE CASCADE,
    FOREIGN KEY (support_model_id) REFERENCES support_models(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 支架部件表（依赖 support_models）
CREATE TABLE IF NOT EXISTS stent_parts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_id INT NOT NULL,
    part_name VARCHAR(50),
    part_type VARCHAR(20),
    material VARCHAR(50),
    quantity INT DEFAULT 1,
    FOREIGN KEY (model_id) REFERENCES support_models(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. 参数依赖表（独立表，无外键，任意顺序）
CREATE TABLE IF NOT EXISTS param_dependencies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    param_name VARCHAR(50) NOT NULL,
    param_value VARCHAR(100),
    description TEXT,
    category VARCHAR(30),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
