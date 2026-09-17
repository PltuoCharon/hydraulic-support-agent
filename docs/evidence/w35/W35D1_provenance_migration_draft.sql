-- W35D1 Provenance Schema Draft
-- DRAFT ONLY / DO NOT EXECUTE IN W35D1

CREATE TABLE IF NOT EXISTS evidence_sources (
    id BIGINT NOT NULL AUTO_INCREMENT,
    source_type VARCHAR(30) NOT NULL,
    title VARCHAR(500) NOT NULL,
    authors VARCHAR(500) DEFAULT NULL,
    publication_year SMALLINT DEFAULT NULL,
    publisher VARCHAR(255) DEFAULT NULL,
    url TEXT DEFAULT NULL,
    note TEXT DEFAULT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    KEY idx_evidence_sources_type (source_type),
    KEY idx_evidence_sources_year (publication_year)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE IF NOT EXISTS parameter_evidence (
    id BIGINT NOT NULL AUTO_INCREMENT,

    support_id INT NOT NULL,
    field_name VARCHAR(64) NOT NULL,

    value_text VARCHAR(500) DEFAULT NULL,
    value_num DECIMAL(20,6) DEFAULT NULL,
    value_min DECIMAL(20,6) DEFAULT NULL,
    value_max DECIMAL(20,6) DEFAULT NULL,
    unit VARCHAR(32) DEFAULT NULL,

    value_origin VARCHAR(20) NOT NULL,
    verification_status VARCHAR(20) NOT NULL,

    source_id BIGINT DEFAULT NULL,
    source_locator VARCHAR(255) DEFAULT NULL,
    formula_id VARCHAR(32) DEFAULT NULL,

    is_derived TINYINT(1) NOT NULL DEFAULT 0,
    is_selected TINYINT(1) NOT NULL DEFAULT 0,

    note TEXT DEFAULT NULL,

    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    KEY idx_parameter_evidence_support (support_id),
    KEY idx_parameter_evidence_field (support_id, field_name),
    KEY idx_parameter_evidence_source (source_id),

    CONSTRAINT fk_parameter_evidence_support
        FOREIGN KEY (support_id)
        REFERENCES support_models (id)
        ON DELETE CASCADE,

    CONSTRAINT fk_parameter_evidence_source
        FOREIGN KEY (source_id)
        REFERENCES evidence_sources (id)
        ON DELETE SET NULL,

    CONSTRAINT chk_parameter_evidence_origin
        CHECK (
            value_origin IN (
                'original',
                'supplemented',
                'calculated',
                'estimated',
                'missing'
            )
        ),

    CONSTRAINT chk_parameter_evidence_verification
        CHECK (
            verification_status IN (
                'verified',
                'provisional',
                'conflicting',
                'unverified'
            )
        ),

    CONSTRAINT chk_parameter_evidence_range
        CHECK (
            value_min IS NULL
            OR value_max IS NULL
            OR value_min <= value_max
        )
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;

-- W35D1 deliberately does not:
-- ALTER support_models
-- INSERT provenance data
-- UPDATE support_models
-- DELETE legacy source
-- create a formula_id foreign key
