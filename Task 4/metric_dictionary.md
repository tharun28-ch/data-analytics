# Metric Dictionary: Application Funnel

Every number on the Application Funnel dashboard traces back to a specific event or database state. This ensures trust, reproducibility, and a direct tie to business decisions.

## 1. Top-Level Funnel Metrics

### Jobs Viewed
- **Definition:** The total number of times a student viewed a job detail page.
- **Source:** `events` table where `event_type = 'student_viewed_job'`.
- **Decision Tie:** Indicates top-of-funnel discovery. If views are low, search or recommendations need improvement.

### Applications Submitted
- **Definition:** The total number of job applications successfully submitted by students.
- **Source:** `events` table where `event_type = 'application_submitted'`.
- **Decision Tie:** Measures intent. If views are high but applications are low, the jobs may be unappealing or the application process too much friction.

### Candidates Shortlisted
- **Definition:** The total number of applications marked as 'shortlisted' by companies.
- **Source:** `events` table where `event_type = 'company_shortlisted'`.
- **Decision Tie:** Measures quality of match. If applications are high but shortlists are low, the marketplace is generating noise (poor fit candidates).

### Applications Rejected
- **Definition:** The total number of applications explicitly rejected by companies.
- **Source:** `events` table where `event_type = 'company_rejected'`.
- **Decision Tie:** Helps close the loop for candidates. High explicit rejection rates for low-fit candidates means the matching engine needs to filter better upstream.

## 2. Candidate Quality Metrics

### Meets Threshold vs Below Threshold
- **Definition:** Applications categorized by whether the candidate's `fit_score` at the time of application meets or exceeds the job's `skill_threshold`.
- **Source:** Joined query between `applications.fit_score` and `jobs.skill_threshold`.
- **Decision Tie:** Answers the critical question: *"When a student doesn't meet the skill threshold, what exactly happens to them?"*. If below-threshold candidates have a 0% shortlist rate, we should consider hard-blocking them from applying to save company review time.

### Shortlist Rate
- **Definition:** The percentage of total applications in a category that resulted in a shortlist. `(shortlisted / total_applications) * 100`.
- **Source:** Calculated from `applications` table group by statuses.
- **Decision Tie:** Defines the "success" rate of an application. 

## 3. Data Quality Checks

### Event Freshness
- **Definition:** Verifies that events have been ingested into the pipeline within the last 60 minutes.
- **Source:** `SELECT COUNT(*) FROM events WHERE ingested_at >= datetime('now','-1 hour')`
- **Decision Tie:** Ensures the founder is looking at live data. If this fails, the dashboard displays an error and data should not be trusted for immediate decisions.

### Null IDs in Applications
- **Definition:** Checks if any application records are missing a `job_id` or `student_id`.
- **Source:** `SELECT COUNT(*) FROM applications WHERE job_id IS NULL OR student_id IS NULL`
- **Decision Tie:** Data integrity sanity check. Prevents orphaned data from silently skewing conversion metrics.
