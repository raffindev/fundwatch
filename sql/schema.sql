-- ============================================================
-- FUNDWATCH v0.1
-- PostgreSQL 18+
-- Schema inicial do banco de dados
-- ============================================================
CREATE SCHEMA IF NOT EXISTS fundwatch;

-- ============================================================
-- 1. CONTROLE DE IMPORTACOES
-- ============================================================
CREATE TABLE fundwatch.import_runs (
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

-- Impede mais de uma importacao ativa ou concluida
-- com sucesso para o mesmo hash.
CREATE UNIQUE INDEX uq_import_runs_active_file_hash ON fundwatch.import_runs (file_hash)
WHERE
    status IN ('PROCESSING', 'SUCCESS');

-- ============================================================
-- 2. AUDITORIA DAS TENTATIVAS DE IMPORTACAO
-- ============================================================
CREATE TABLE fundwatch.import_attempts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_hash CHAR(64) NOT NULL,
    requested_by VARCHAR(100),
    target_table VARCHAR(100) NOT NULL,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    outcome VARCHAR(30) NOT NULL CHECK (
        outcome IN ('ACCEPTED', 'ALREADY_IMPORTED', 'REJECTED')
    ),
    import_run_id BIGINT REFERENCES fundwatch.import_runs (id),
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

-- ============================================================
-- 3. FUNDOS DE INVESTIMENTO
-- ============================================================
CREATE TABLE fundwatch.funds (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cnpj VARCHAR(18) NOT NULL UNIQUE,
    class_type VARCHAR(30) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. REVISOES DOS INFORMES
-- ============================================================
CREATE TABLE fundwatch.revisions (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id BIGINT NOT NULL,
    reference_date DATE NOT NULL,
    note TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_revisions_import_run FOREIGN KEY (run_id) REFERENCES fundwatch.import_runs (id)
);

-- ============================================================
-- 5. INFORMES DIARIOS
-- ============================================================
CREATE TABLE fundwatch.daily_reports (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fund_id BIGINT NOT NULL,
    subclass_id VARCHAR(15),
    reference_date DATE NOT NULL,
    total_value NUMERIC(17, 2),
    quota_value NUMERIC(27, 12),
    net_equity NUMERIC(17, 2),
    inflow NUMERIC(17, 2),
    outflow NUMERIC(17, 2),
    shareholders INTEGER,
    revision_id BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    import_run_id BIGINT NOT NULL REFERENCES fundwatch.import_runs (id),
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_daily_reports_fund FOREIGN KEY (fund_id) REFERENCES fundwatch.funds (id),
    CONSTRAINT fk_daily_reports_revision FOREIGN KEY (revision_id) REFERENCES fundwatch.revisions (id)
);

-- ============================================================
-- 6. UNICIDADE POR IMPORTACAO
-- ============================================================
-- Impede duplicidades da mesma chave logica
-- dentro de uma importacao.
-- NULLS NOT DISTINCT considera subclasses NULL iguais.
CREATE UNIQUE INDEX uq_daily_reports_import_record ON fundwatch.daily_reports (
    import_run_id,
    fund_id,
    reference_date,
    subclass_id
) NULLS NOT DISTINCT;

-- ============================================================
-- 7. UNICIDADE DA VERSAO VIGENTE
-- ============================================================
-- Permite varias versoes historicas,
-- mas apenas uma versao vigente por chave logica.
CREATE UNIQUE INDEX uq_daily_reports_current ON fundwatch.daily_reports (fund_id, reference_date, subclass_id) NULLS NOT DISTINCT
WHERE
    is_current = TRUE;
