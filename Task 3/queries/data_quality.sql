-- ============================================================
-- PlaceMux · Data Quality Checks
-- queries/data_quality.sql
--
-- Run these checks after each pipeline run.
-- All checks return: check_name, status (pass/warn/fail), value, threshold, details
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- CHECK 1: Event freshness — last event ingested within 1 hour
-- FAIL if no events in last hour (pipeline may be broken)
-- ─────────────────────────────────────────────────────────────
SELECT
    'event_freshness_1h'                                    AS check_name,
    'freshness'                                             AS check_type,
    COUNT(*)                                                AS value,
    1                                                       AS threshold,
    CASE WHEN COUNT(*) >= 1 THEN 'pass' ELSE 'fail' END    AS status,
    'Events ingested in the last 60 minutes'                AS details,
    MAX(ingested_at)                                        AS last_event_at
FROM events
WHERE ingested_at >= datetime('now', '-1 hour');

-- ─────────────────────────────────────────────────────────────
-- CHECK 2: Null job_id on view/apply events
-- WARN if any view or apply event has no job_id
-- ─────────────────────────────────────────────────────────────
SELECT
    'null_job_id_view_apply'                                AS check_name,
    'null_check'                                            AS check_type,
    COUNT(*)                                                AS value,
    0                                                       AS threshold,
    CASE WHEN COUNT(*) = 0 THEN 'pass'
         WHEN COUNT(*) < 10 THEN 'warn'
         ELSE 'fail' END                                    AS status,
    'view/apply events missing job_id'                      AS details,
    NULL                                                    AS last_event_at
FROM events
WHERE event_type IN ('student_viewed_job', 'application_submitted')
  AND job_id IS NULL;

-- ─────────────────────────────────────────────────────────────
-- CHECK 3: Duplicate applications (same student+job)
-- WARN if any duplicates exist
-- ─────────────────────────────────────────────────────────────
SELECT
    'duplicate_applications'                                AS check_name,
    'duplicate'                                             AS check_type,
    COUNT(*)                                                AS value,
    0                                                       AS threshold,
    CASE WHEN COUNT(*) = 0 THEN 'pass' ELSE 'warn' END     AS status,
    'student+job pairs with >1 application'                 AS details,
    NULL                                                    AS last_event_at
FROM (
    SELECT student_id, job_id, COUNT(*) AS cnt
    FROM applications
    GROUP BY student_id, job_id
    HAVING cnt > 1
);

-- ─────────────────────────────────────────────────────────────
-- CHECK 4: Fit score range sanity
-- FAIL if any fit score is outside [0, 100]
-- ─────────────────────────────────────────────────────────────
SELECT
    'fit_score_range'                                       AS check_name,
    'sanity'                                                AS check_type,
    COUNT(*)                                                AS value,
    0                                                       AS threshold,
    CASE WHEN COUNT(*) = 0 THEN 'pass' ELSE 'fail' END     AS status,
    'applications with fit_score outside [0,100]'           AS details,
    NULL                                                    AS last_event_at
FROM applications
WHERE fit_score < 0 OR fit_score > 100;

-- ─────────────────────────────────────────────────────────────
-- CHECK 5: Jobs with no skills defined
-- WARN if active jobs lack required skills (search ranking breaks)
-- ─────────────────────────────────────────────────────────────
SELECT
    'jobs_missing_skills'                                   AS check_name,
    'sanity'                                                AS check_type,
    COUNT(*)                                                AS value,
    0                                                       AS threshold,
    CASE WHEN COUNT(*) = 0 THEN 'pass'
         WHEN COUNT(*) < 5 THEN 'warn'
         ELSE 'fail' END                                    AS status,
    'active jobs with no job_skills entries'                AS details,
    NULL                                                    AS last_event_at
FROM jobs j
WHERE j.is_active = 1
  AND NOT EXISTS (SELECT 1 FROM job_skills js WHERE js.job_id = j.job_id);

-- ─────────────────────────────────────────────────────────────
-- CHECK 6: Zero-result searches (discovery failure)
-- WARN if >30% of searches return 0 results (broken ranking/index)
-- ─────────────────────────────────────────────────────────────
SELECT
    'zero_result_searches'                                  AS check_name,
    'sanity'                                                AS check_type,
    ROUND(
        SUM(CASE WHEN results_count = 0 THEN 1.0 ELSE 0 END)
        / COUNT(*) * 100, 1
    )                                                       AS value,
    30                                                      AS threshold,
    CASE WHEN
        SUM(CASE WHEN results_count = 0 THEN 1.0 ELSE 0 END) / COUNT(*) < 0.3
        THEN 'pass'
        WHEN
        SUM(CASE WHEN results_count = 0 THEN 1.0 ELSE 0 END) / COUNT(*) < 0.5
        THEN 'warn'
        ELSE 'fail'
    END                                                     AS status,
    'pct of searches returning 0 results'                   AS details,
    NULL                                                    AS last_event_at
FROM search_logs
WHERE searched_at >= datetime('now', '-24 hours');

-- ─────────────────────────────────────────────────────────────
-- CHECK 7: Application event ↔ applications table consistency
-- WARN if event count vs table count differs by >5%
-- ─────────────────────────────────────────────────────────────
SELECT
    'event_table_consistency'                               AS check_name,
    'sanity'                                                AS check_type,
    ABS(
        (SELECT COUNT(*) FROM events WHERE event_type='application_submitted')
        - (SELECT COUNT(*) FROM applications)
    )                                                       AS value,
    ROUND(
        ABS(
            (SELECT COUNT(*) FROM events WHERE event_type='application_submitted')
            - (SELECT COUNT(*) FROM applications)
        ) * 100.0 / MAX(
            (SELECT COUNT(*) FROM applications), 1
        ), 1
    )                                                       AS discrepancy_pct,
    CASE WHEN
        ABS(
            (SELECT COUNT(*) FROM events WHERE event_type='application_submitted')
            - (SELECT COUNT(*) FROM applications)
        ) * 100.0 / MAX((SELECT COUNT(*) FROM applications),1) <= 5
        THEN 'pass' ELSE 'warn'
    END                                                     AS status,
    'diff between application events and applications table rows' AS details,
    NULL                                                    AS last_event_at;
