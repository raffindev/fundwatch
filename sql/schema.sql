CREATE TABLE import_runs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_hash CHAR(64),
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL CHECK (
        status IN ('PROCESSING', 'SUCCESS', 'FAILED', 'REJECTED')
    ),
    error_message TEXT,
    total_records INT CHECK (total_records >= 0),
    duplicates INT CHECK (duplicates >= 0),
    missing_subclass INT CHECK (missing_subclass >= 0),
    CHECK (finished_at >= started_at)
);