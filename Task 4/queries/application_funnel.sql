-- ============================================================
-- PlaceMux · Application Funnel Analytics Queries
-- ============================================================
-- These queries power the Application Funnel dashboard.
-- ============================================================

-- ─────────────────────────────────────────
-- 1. Application Funnel Stages
-- ─────────────────────────────────────────
-- Tracks the volume drop-off from a student viewing a job to the
-- final decision (shortlisted or rejected).
WITH
s1 AS (SELECT COUNT(*) n FROM events WHERE event_type='student_viewed_job'),
s2 AS (SELECT COUNT(*) n FROM events WHERE event_type='application_submitted'),
s3 AS (SELECT COUNT(*) n FROM events WHERE event_type='company_shortlisted'),
s4 AS (SELECT COUNT(*) n FROM events WHERE event_type='company_rejected')
SELECT
    (SELECT n FROM s1) AS jobs_viewed,
    (SELECT n FROM s2) AS applications_submitted,
    (SELECT n FROM s3) AS candidates_shortlisted,
    (SELECT n FROM s4) AS candidates_rejected;

-- ─────────────────────────────────────────
-- 2. Candidate Quality vs. Skill Threshold
-- ─────────────────────────────────────────
-- Determines how well the candidate fit score aligns with the
-- job's skill threshold, and the resulting shortlist/rejection rates.
SELECT 
    CASE 
        WHEN a.fit_score >= j.skill_threshold THEN 'Meets Threshold'
        ELSE 'Below Threshold'
    END as category,
    COUNT(*) as total_applications,
    SUM(CASE WHEN a.status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted,
    SUM(CASE WHEN a.status = 'rejected' THEN 1 ELSE 0 END) as rejected,
    SUM(CASE WHEN a.status = 'applied' THEN 1 ELSE 0 END) as pending,
    -- Shortlist rate calculation
    ROUND(SUM(CASE WHEN a.status = 'shortlisted' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS shortlist_rate_pct
FROM applications a
JOIN jobs j ON a.job_id = j.job_id
GROUP BY category;

-- ─────────────────────────────────────────
-- 3. Application Trend (Daily)
-- ─────────────────────────────────────────
-- 30-day view of application submission and processing velocity.
SELECT
    DATE(occurred_at) AS event_date,
    SUM(CASE WHEN event_type='application_submitted' THEN 1 ELSE 0 END) AS applications,
    SUM(CASE WHEN event_type='company_shortlisted' THEN 1 ELSE 0 END) AS shortlisted,
    SUM(CASE WHEN event_type='company_rejected' THEN 1 ELSE 0 END) AS rejected
FROM events
WHERE occurred_at >= datetime('now', '-30 days')
GROUP BY DATE(occurred_at)
ORDER BY event_date;
