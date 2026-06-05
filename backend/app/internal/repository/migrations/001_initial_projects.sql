CREATE TABLE IF NOT EXISTS projects (
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT,
    project_type TEXT,
    total_cost_rub NUMERIC(14, 2),
    duration_weeks INTEGER,
    team_size INTEGER,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    input_project TEXT,
    estimation TEXT,
    llm_analysis TEXT
);

CREATE TABLE IF NOT EXISTS projects_archive (
    id BIGINT PRIMARY KEY,
    project_name TEXT,
    project_type TEXT,
    total_cost_rub NUMERIC(14, 2),
    duration_weeks INTEGER,
    team_size INTEGER,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    input_project TEXT,
    estimation TEXT,
    llm_analysis TEXT
);

CREATE INDEX IF NOT EXISTS idx_projects_generated_at
    ON projects (generated_at DESC);

CREATE INDEX IF NOT EXISTS idx_projects_archive_generated_at
    ON projects_archive (generated_at DESC);
