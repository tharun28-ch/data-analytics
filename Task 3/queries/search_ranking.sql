-- ============================================================
-- PlaceMux · Job Search Ranking Query
-- queries/search_ranking.sql
--
-- METRIC: Fit Score (ranked job search results)
-- FORMULA: fit_score = skill_match_score * 0.7 + recency_score * 0.3
-- SOURCE: job_skills, student_skills, jobs
-- DECISION: Which jobs to surface to a student; below skill_threshold = filtered out
-- ============================================================

-- ─────────────────────────────────────────────────────────────
-- Parameters (replace with actual values at query time):
--   :student_id   = student performing the search
--   :query_text   = keyword typed (matched against job title/skill name)
-- ─────────────────────────────────────────────────────────────

WITH
-- Step 1: Student's skills with proficiency
student_profile AS (
    SELECT
        ss.skill_id,
        ss.proficiency,
        s.skill_name
    FROM student_skills ss
    JOIN skills s ON s.skill_id = ss.skill_id
    WHERE ss.student_id = :student_id
),

-- Step 2: For each job, compute total required weight and matched weight
job_skill_match AS (
    SELECT
        js.job_id,
        SUM(js.weight)                                               AS total_weight,
        SUM(
            CASE WHEN sp.skill_id IS NOT NULL
                 THEN js.weight * (sp.proficiency / 5.0)
                 WHEN js.is_mandatory = 1 THEN -js.weight * 0.5    -- penalty for missing mandatory
                 ELSE 0
            END
        )                                                            AS matched_weight,
        COUNT(DISTINCT js.skill_id)                                  AS required_skill_count,
        COUNT(DISTINCT sp.skill_id)                                  AS matched_skill_count
    FROM job_skills js
    LEFT JOIN student_profile sp ON sp.skill_id = js.skill_id
    GROUP BY js.job_id
),

-- Step 3: Compute recency score (1.0 = today, 0.0 = 30 days ago)
job_recency AS (
    SELECT
        job_id,
        ROUND(
            1.0 - (julianday('now') - julianday(posted_at)) / 30.0,
            3
        ) AS recency_score
    FROM jobs
    WHERE is_active = 1
),

-- Step 4: Combine into fit score
scored_jobs AS (
    SELECT
        j.job_id,
        j.company_id,
        j.title,
        j.job_type,
        j.location,
        j.salary_min,
        j.salary_max,
        j.skill_threshold,
        j.posted_at,
        c.name                                                       AS company_name,
        c.industry,

        ROUND(GREATEST(0, LEAST(100,
            (jsm.matched_weight / NULLIF(jsm.total_weight, 0)) * 100
        )), 1)                                                       AS skill_score,

        ROUND(GREATEST(0, LEAST(1.0, jr.recency_score)), 3)         AS recency_score,

        -- Final fit score: weighted combination
        ROUND(GREATEST(0, LEAST(100,
            (GREATEST(0, LEAST(100,
                (jsm.matched_weight / NULLIF(jsm.total_weight, 0)) * 100
            )) * 0.70)
            + (GREATEST(0, LEAST(1.0, jr.recency_score)) * 100 * 0.30)
        )), 1)                                                       AS fit_score,

        jsm.required_skill_count,
        jsm.matched_skill_count,
        -- List of matched skill names (comma-separated)
        GROUP_CONCAT(DISTINCT
            CASE WHEN sp.skill_id IS NOT NULL THEN sp.skill_name END
        )                                                            AS matched_skills

    FROM jobs j
    JOIN companies c ON c.company_id = j.company_id
    JOIN job_skill_match jsm ON jsm.job_id = j.job_id
    JOIN job_recency jr ON jr.job_id = j.job_id
    LEFT JOIN job_skills js2 ON js2.job_id = j.job_id
    LEFT JOIN student_profile sp ON sp.skill_id = js2.skill_id

    WHERE j.is_active = 1
    GROUP BY j.job_id
)

SELECT
    job_id,
    company_id,
    company_name,
    industry,
    title,
    job_type,
    location,
    salary_min,
    salary_max,
    skill_threshold,
    posted_at,
    skill_score,
    recency_score,
    fit_score,
    required_skill_count,
    matched_skill_count,
    matched_skills,

    -- Threshold gate: student passes if fit_score >= skill_threshold
    CASE WHEN fit_score >= skill_threshold THEN 1 ELSE 0 END         AS meets_threshold,

    -- Rank within threshold-passing jobs (DECISION: show only these to student)
    RANK() OVER (ORDER BY
        CASE WHEN fit_score >= skill_threshold THEN 0 ELSE 1 END,
        fit_score DESC
    )                                                                 AS search_rank

FROM scored_jobs

-- Optional keyword filter (remove WHERE clause to return all results)
WHERE (
    :query_text = ''
    OR LOWER(title) LIKE '%' || LOWER(:query_text) || '%'
    OR LOWER(matched_skills) LIKE '%' || LOWER(:query_text) || '%'
    OR LOWER(company_name) LIKE '%' || LOWER(:query_text) || '%'
    OR LOWER(industry) LIKE '%' || LOWER(:query_text) || '%'
)

ORDER BY
    meets_threshold DESC,   -- threshold-passing jobs first
    fit_score DESC          -- then by fit score
LIMIT 50;


-- ─────────────────────────────────────────────────────────────
-- SECTION 2: Threshold filter analysis
-- Shows what happens to students below the threshold
-- DECISION: Are we being too restrictive? Too lenient?
-- ─────────────────────────────────────────────────────────────
SELECT
    j.skill_threshold,
    COUNT(DISTINCT a.application_id)                    AS total_applications,
    COUNT(DISTINCT CASE WHEN a.fit_score >= j.skill_threshold
                        THEN a.application_id END)      AS above_threshold,
    COUNT(DISTINCT CASE WHEN a.fit_score < j.skill_threshold
                        THEN a.application_id END)      AS below_threshold,
    ROUND(AVG(a.fit_score), 1)                          AS avg_fit_score,
    ROUND(AVG(CASE WHEN a.status = 'shortlisted'
                   THEN 1.0 ELSE 0.0 END) * 100, 1)    AS shortlist_rate_pct
FROM applications a
JOIN jobs j ON j.job_id = a.job_id
GROUP BY j.skill_threshold
ORDER BY j.skill_threshold;
