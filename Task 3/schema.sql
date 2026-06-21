-- ============================================================
-- PlaceMux · Company Funnel Analytics · Database Schema
-- ============================================================
-- All timestamps stored as ISO-8601 TEXT (UTC).
-- SQLite-compatible; replace TEXT/REAL with appropriate types
-- if migrating to PostgreSQL.
-- ============================================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- ─────────────────────────────────────────
-- 1. COMPANIES
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS companies (
    company_id      TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    industry        TEXT NOT NULL,
    size            TEXT NOT NULL CHECK(size IN ('startup','sme','enterprise')),
    location        TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1
);

-- ─────────────────────────────────────────
-- 2. JOBS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    job_id          TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL REFERENCES companies(company_id),
    title           TEXT NOT NULL,
    description     TEXT,
    location        TEXT NOT NULL,
    job_type        TEXT NOT NULL CHECK(job_type IN ('full_time','internship','contract')),
    salary_min      REAL,
    salary_max      REAL,
    experience_min  INTEGER NOT NULL DEFAULT 0,   -- years
    skill_threshold INTEGER NOT NULL DEFAULT 60,  -- minimum fit score (0-100) to appear in search
    posted_at       TEXT NOT NULL,
    expires_at      TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1
);

-- ─────────────────────────────────────────
-- 3. SKILLS (shared lookup)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS skills (
    skill_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name      TEXT NOT NULL UNIQUE,
    category        TEXT NOT NULL  -- e.g. 'technical','soft','domain'
);

-- ─────────────────────────────────────────
-- 4. JOB SKILLS (required skills per job)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_skills (
    job_id          TEXT NOT NULL REFERENCES jobs(job_id),
    skill_id        INTEGER NOT NULL REFERENCES skills(skill_id),
    weight          REAL NOT NULL DEFAULT 1.0,  -- importance multiplier
    is_mandatory    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (job_id, skill_id)
);

-- ─────────────────────────────────────────
-- 5. STUDENTS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    student_id      TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    college         TEXT NOT NULL,
    degree          TEXT NOT NULL,
    graduation_year INTEGER NOT NULL,
    location        TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1
);

-- ─────────────────────────────────────────
-- 6. STUDENT SKILLS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS student_skills (
    student_id      TEXT NOT NULL REFERENCES students(student_id),
    skill_id        INTEGER NOT NULL REFERENCES skills(skill_id),
    proficiency     INTEGER NOT NULL CHECK(proficiency BETWEEN 1 AND 5),  -- 1=beginner, 5=expert
    PRIMARY KEY (student_id, skill_id)
);

-- ─────────────────────────────────────────
-- 7. EVENTS (analytics event log)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    event_id        TEXT PRIMARY KEY,
    event_type      TEXT NOT NULL,        -- see taxonomy below
    actor_type      TEXT NOT NULL CHECK(actor_type IN ('company','student','system')),
    actor_id        TEXT NOT NULL,
    session_id      TEXT,
    job_id          TEXT,                 -- nullable; set when event is job-specific
    company_id      TEXT,                 -- nullable; denormalized for fast funnel queries
    student_id      TEXT,                 -- nullable; set when actor or subject is a student
    properties      TEXT,                 -- JSON blob for additional metadata
    occurred_at     TEXT NOT NULL,        -- ISO-8601 UTC
    ingested_at     TEXT NOT NULL         -- when the pipeline received it
);

-- Event taxonomy (values for event_type):
--   company_signed_up        → company creates account
--   company_posted_job       → company posts a new job listing
--   company_edited_job       → company edits an existing listing
--   company_viewed_candidates→ company views candidate list for a job
--   company_shortlisted      → company marks a student as shortlisted
--   company_rejected         → company rejects a student
--   student_signed_up        → student creates account
--   student_searched_jobs    → student performs a search query
--   student_viewed_job       → student opens a job detail page
--   application_submitted    → student applies to a job
--   application_withdrawn    → student withdraws an application

-- ─────────────────────────────────────────
-- 8. APPLICATIONS
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS applications (
    application_id  TEXT PRIMARY KEY,
    job_id          TEXT NOT NULL REFERENCES jobs(job_id),
    student_id      TEXT NOT NULL REFERENCES students(student_id),
    company_id      TEXT NOT NULL REFERENCES companies(company_id),
    fit_score       REAL NOT NULL,        -- 0-100 at time of application
    status          TEXT NOT NULL DEFAULT 'applied'
                    CHECK(status IN ('applied','shortlisted','rejected','withdrawn')),
    applied_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- ─────────────────────────────────────────
-- 9. SEARCH LOGS (dedicated for ranking analysis)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS search_logs (
    search_id       TEXT PRIMARY KEY,
    student_id      TEXT NOT NULL REFERENCES students(student_id),
    session_id      TEXT NOT NULL,
    query_text      TEXT,
    filters         TEXT,                 -- JSON: {skills, location, job_type, ...}
    results_count   INTEGER NOT NULL DEFAULT 0,
    top_fit_score   REAL,
    searched_at     TEXT NOT NULL
);

-- ─────────────────────────────────────────
-- 10. DATA QUALITY LOG
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS data_quality_log (
    check_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    check_name      TEXT NOT NULL,
    check_type      TEXT NOT NULL CHECK(check_type IN ('freshness','null_check','duplicate','sanity')),
    status          TEXT NOT NULL CHECK(status IN ('pass','warn','fail')),
    details         TEXT,
    checked_at      TEXT NOT NULL
);

-- ─────────────────────────────────────────
-- INDEXES for performance
-- ─────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_events_type        ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_actor       ON events(actor_id, actor_type);
CREATE INDEX IF NOT EXISTS idx_events_occurred    ON events(occurred_at);
CREATE INDEX IF NOT EXISTS idx_events_job         ON events(job_id);
CREATE INDEX IF NOT EXISTS idx_events_company     ON events(company_id);
CREATE INDEX IF NOT EXISTS idx_applications_job   ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_stu   ON applications(student_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_jobs_company       ON jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_active        ON jobs(is_active, posted_at);
CREATE INDEX IF NOT EXISTS idx_search_student     ON search_logs(student_id, searched_at);
