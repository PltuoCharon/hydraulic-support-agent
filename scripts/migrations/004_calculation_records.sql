-- W35-D4 calculation record persistence
CREATE TABLE IF NOT EXISTS calculation_records (
  id INT AUTO_INCREMENT PRIMARY KEY,
  record_version INT NOT NULL DEFAULT 1,
  calc_type VARCHAR(50) NOT NULL,
  run_mode VARCHAR(20) NOT NULL,
  formula_ids TEXT NOT NULL,
  inputs_snapshot TEXT NOT NULL,
  outputs_snapshot TEXT NOT NULL,
  context_source_type VARCHAR(40) NULL,
  context_confirmed TINYINT(1) NULL,
  context_snapshot TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_calculation_records_type (calc_type),
  INDEX idx_calculation_records_created (created_at),
  INDEX idx_calculation_records_context (context_source_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='W35-D4 calculation trace records';
