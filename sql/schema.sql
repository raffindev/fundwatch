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

CREATE TABLE import_attempts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_hash CHAR(64) NOT NULL,
    requested_by VARCHAR(100),
    target_table VARCHAR(100) NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    outcome VARCHAR(30) NOT NULL CHECK (
        outcome IN ('ACCEPTED', 'ALREADY_IMPORTED', 'REJECTED')
    ),
    import_run_id BIGINT REFERENCES import_runs (id),
    reason TEXT,
    CONSTRAINT accepted_attempt_requires_run CHECK (
        outcome <> 'ACCEPTED'
        OR import_run_id IS NOT NULL
    ),
    CONSTRAINT refused_attempt_has_no_run CHECK (
        outcome = 'ACCEPTED'
        OR import_run_id IS NULL
    )
);