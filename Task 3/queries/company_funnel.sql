-- ============================================================
-- PlaceMux · Company Funnel Analytics Query
-- queries/company_funnel.sql
--
-- METRIC: Company Funnel
-- SOURCE: events table + applications + jobs + companies
-- DECISION: Is the marketplace working? Where are users dropping?
-- OWNER: Data Analyst
-- LAST UPDATED: 2026-06-21
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- SECTION 1: Overall funnel — last 30 days
-- Returns one row per funnel stage with count and drop-off rate
-- ─────────────────────────────────────────────────────────────
WITH
-- Stage 1: Companies that signed up
companies_signed_up AS (
    SELECT COUNT(DISTINCT actor_id) AS n
    FROM events
    WHERE event_type = 'company_signed_up'
      AND occurred_at >= datetime('now', '-30 days')
),
-- Stage 2: Companies that posted at least one job
companies_posted_job AS (
    SELECT COUNT(DISTINCT company_id) AS n
    FROM events
    WHERE event_type = 'company_posted_job'
      AND occurred_at >= datetime('now', '-30 days')
),
-- Stage 3: Active jobs that were discovered (appeared in ≥1 search result)
-- Proxy: jobs that received at least one student_viewed_job event
jobs_discovered AS (
    SELECT COUNT(DISTINCT job_id) AS n
    FROM events
    WHERE event_type = 'student_viewed_job'
      AND occurred_at >= datetime('now', '-30 days')
),
-- Stage 4: Students who searched (discovery demand side)
students_searched AS (
    SELECT COUNT(DISTINCT student_id) AS n
    FROM events
    WHERE event_type = 'student_searched_jobs'
      AND occurred_at >= datetime('now', '-30 days')
),
-- Stage 5: Job views (total)
total_job_views AS (
    SELECT COUNT(*) AS n
    FROM events
    WHERE event_type = 'student_viewed_job'
      AND occurred_at >= datetime('now', '-30 days')
),
-- Stage 6: Applications submitted
applications_submitted AS (
    SELECT COUNT(*) AS n
    FROM events
    WHERE event_type = 'application_submitted'
      AND occurred_at >= datetime('now', '-30 days')
),
-- Stage 7: Candidates shortlisted
candidates_shortlisted AS (
    SELECT COUNT(*) AS n
    FROM events
    WHERE event_type = 'company_shortlisted'
      AND occurred_at >= datetime('now', '-30 days')
),
-- All stages combined for drop-off calculation
stages AS (
    SELECT
        'companies_signed_up'   AS stage, 1 AS stage_order, (SELECT n FROM companies_signed_up)   AS count
    UNION ALL SELECT
        'companies_posted_job',  2,                          (SELECT n FROM companies_posted_job)
    UNION ALL SELECT
        'students_searched',     3,                          (SELECT n FROM students_searched)
    UNION ALL SELECT
        'jobs_viewed_unique',    4,                          (SELECT n FROM jobs_discovered)
    UNION ALL SELECT
        'total_job_views',       5,                          (SELECT n FROM total_job_views)
    UNION ALL SELECT
        'applications_submitted',6,                          (SELECT n FROM applications_submitted)
    UNION ALL SELECT
        'candidates_shortlisted',7,                          (SELECT n FROM candidates_shortlisted)
)
SELECT
    stage,
    stage_order,
    count,
    LAG(count) OVER (ORDER BY stage_order) AS prev_stage_count,
    CASE
        WHEN LAG(count) OVER (ORDER BY stage_order) IS NULL THEN NULL
        WHEN LAG(count) OVER (ORDER BY stage_order) = 0     THEN NULL
        ELSE ROUND(
            (count * 100.0) / LAG(count) OVER (ORDER BY stage_order), 1
        )
    END AS conversion_pct
FROM stages
ORDER BY stage_order;


-- ─────────────────────────────────────────────────────────────
-- SECTION 2: Per-company funnel (leaderboard)
-- Shows each company's jobs posted, views received, applications, shortlists
-- ─────────────────────────────────────────────────────────────
SELECT
    c.company_id,
    c.name            AS company_name,
    c.industry,
    c.size,

    -- Jobs posted (last 30 days)
    COUNT(DISTINCT CASE WHEN e.event_type = 'company_posted_job'
                         AND e.occurred_at >= datetime('now', '-30 days')
                    THEN e.job_id END)                                   AS jobs_posted,

    -- Unique students who viewed their jobs
    COUNT(DISTINCT CASE WHEN e.event_type = 'student_viewed_job'
                         AND e.occurred_at >= datetime('now', '-30 days')
                    THEN e.student_id END)                               AS unique_viewers,

    -- Total job views
    COUNT(CASE WHEN e.event_type = 'student_viewed_job'
                AND e.occurred_at >= datetime('now', '-30 days')
          THEN 1 END)                                                    AS total_views,

    -- Applications received
    COUNT(CASE WHEN e.event_type = 'application_submitted'
                AND e.occurred_at >= datetime('now', '-30 days')
          THEN 1 END)                                                    AS applications_received,

    -- Shortlisted candidates
    COUNT(CASE WHEN e.event_type = 'company_shortlisted'
                AND e.occurred_at >= datetime('now', '-30 days')
          THEN 1 END)                                                    AS shortlisted,

    -- Average fit score of applicants
    ROUND(AVG(CASE WHEN e.event_type = 'application_submitted'
                   THEN CAST(json_extract(e.properties, '$.fit_score') AS REAL)
              END), 1)                                                   AS avg_fit_score,

    -- View-to-application rate (%)
    CASE WHEN COUNT(CASE WHEN e.event_type = 'student_viewed_job' THEN 1 END) = 0 THEN 0
         ELSE ROUND(
             COUNT(CASE WHEN e.event_type = 'application_submitted' THEN 1 END) * 100.0
             / COUNT(CASE WHEN e.event_type = 'student_viewed_job' THEN 1 END), 1)
    END                                                                  AS view_to_apply_pct

FROM companies c
LEFT JOIN events e ON e.company_id = c.company_id
GROUP BY c.company_id, c.name, c.industry, c.size
HAVING jobs_posted > 0
ORDER BY applications_received DESC;


-- ─────────────────────────────────────────────────────────────
-- SECTION 3: Daily funnel trend (last 30 days)
-- For sparkline / trend charts in the dashboard
-- ─────────────────────────────────────────────────────────────
SELECT
    DATE(occurred_at)             AS event_date,
    SUM(CASE WHEN event_type = 'company_posted_job'    THEN 1 ELSE 0 END) AS jobs_posted,
    SUM(CASE WHEN event_type = 'student_searched_jobs' THEN 1 ELSE 0 END) AS searches,
    SUM(CASE WHEN event_type = 'student_viewed_job'    THEN 1 ELSE 0 END) AS job_views,
    SUM(CASE WHEN event_type = 'application_submitted' THEN 1 ELSE 0 END) AS applications,
    SUM(CASE WHEN event_type = 'company_shortlisted'   THEN 1 ELSE 0 END) AS shortlisted,
    COUNT(DISTINCT CASE WHEN event_type = 'student_searched_jobs'
                        THEN actor_id END)                                 AS active_students,
    COUNT(DISTINCT CASE WHEN event_type = 'company_posted_job'
                        THEN actor_id END)                                 AS active_companies
FROM events
WHERE occurred_at >= datetime('now', '-30 days')
GROUP BY DATE(occurred_at)
ORDER BY event_date;
