# PlaceMux · Metric Dictionary
**Task 3 · Company Funnel Analytics · Phase 2 Industry Immersion**
*Every number is sourced. Every metric links to a decision.*

---

## How to use this dictionary
For each metric, you can answer:
1. **What is it?** — the definition
2. **Where does it come from?** — the exact SQL / event
3. **What decision does it trigger?** — the founder action

---

## Funnel Metrics

### 1. Companies Signed Up
| Field | Value |
|---|---|
| **Definition** | Count of distinct companies that emitted a `company_signed_up` event |
| **SQL** | `SELECT COUNT(DISTINCT actor_id) FROM events WHERE event_type='company_signed_up' AND occurred_at >= datetime('now','-30 days')` |
| **Source Table** | `events` |
| **Event** | `company_signed_up` |
| **Window** | Rolling 30 days |
| **Grain** | Company |

**Decision**: Is B2B acquisition working? If this number plateaus for 2+ weeks, invest in outreach campaigns, referral programs, or fix onboarding friction.

---

### 2. Companies Posted Job
| Field | Value |
|---|---|
| **Definition** | Count of distinct companies that posted at least one job listing |
| **SQL** | `SELECT COUNT(DISTINCT company_id) FROM events WHERE event_type='company_posted_job' AND occurred_at >= datetime('now','-30 days')` |
| **Source Table** | `events` |
| **Event** | `company_posted_job` |
| **Window** | Rolling 30 days |

**Decision**: Activation rate. If (Companies Posted / Companies Signed Up) < 70%, companies are signing up but not posting — fix the job-posting onboarding UX, add prompts, or send reminder emails.

---

### 3. Students Signed Up
| Field | Value |
|---|---|
| **Definition** | Count of distinct students that emitted a `student_signed_up` event |
| **SQL** | `SELECT COUNT(DISTINCT student_id) FROM events WHERE event_type='student_signed_up' AND occurred_at >= datetime('now','-30 days')` |
| **Source Table** | `events` |
| **Event** | `student_signed_up` |
| **Window** | Rolling 30 days |

**Decision**: Is student acquisition working? Cross-check with companies: student/company ratio should stay > 3:1 for a healthy supply side.

---

### 4. Students Searched
| Field | Value |
|---|---|
| **Definition** | Count of distinct students who performed at least one job search |
| **SQL** | `SELECT COUNT(DISTINCT student_id) FROM events WHERE event_type='student_searched_jobs' AND occurred_at >= datetime('now','-30 days')` |
| **Source Table** | `events` |
| **Event** | `student_searched_jobs` |
| **Window** | Rolling 30 days |

**Decision**: Is discovery alive? If students aren't searching, send job-alert nudges, push notifications, or improve the homepage CTA. Low searches = students don't know there are jobs.

---

### 5. Jobs Viewed (Unique)
| Field | Value |
|---|---|
| **Definition** | Count of distinct jobs that received at least one `student_viewed_job` event |
| **SQL** | `SELECT COUNT(DISTINCT job_id) FROM events WHERE event_type='student_viewed_job' AND occurred_at >= datetime('now','-30 days')` |
| **Source Table** | `events` |
| **Event** | `student_viewed_job` |
| **Window** | Rolling 30 days |

**Decision**: Are search results compelling? If jobs_viewed/jobs_active < 50%, students are searching but not clicking — improve job card display (titles, salary, company name).

---

### 6. Applications Submitted
| Field | Value |
|---|---|
| **Definition** | Total count of `application_submitted` events |
| **SQL** | `SELECT COUNT(*) FROM events WHERE event_type='application_submitted' AND occurred_at >= datetime('now','-30 days')` |
| **Source Table** | `events`, `applications` |
| **Event** | `application_submitted` |
| **Window** | Rolling 30 days |

**Decision**: Is the marketplace transacting? This is the North Star metric for the supply side. If views are high but applications low → job detail page or CTA needs work.

---

### 7. Candidates Shortlisted
| Field | Value |
|---|---|
| **Definition** | Count of `company_shortlisted` events — companies explicitly shortlisting an applicant |
| **SQL** | `SELECT COUNT(*) FROM events WHERE event_type='company_shortlisted' AND occurred_at >= datetime('now','-30 days')` |
| **Source Table** | `events` |
| **Event** | `company_shortlisted` |
| **Window** | Rolling 30 days |

**Decision**: Are companies finding value? Low shortlist rate despite applications → match quality is poor. Re-tune the fit score weights (skill vs. recency balance).

---

## Search & Ranking Metrics

### 8. Fit Score
| Field | Value |
|---|---|
| **Definition** | Per-student per-job relevance score, 0–100 |
| **Formula** | `fit_score = skill_match_score × 0.70 + recency_score × 0.30` |
| **skill_match_score** | `(Σ weight × proficiency/5 for matched skills) / total_weight × 100` |
| **recency_score** | `1 - (days_since_posted / 30)` clamped to [0,1] |
| **Source Tables** | `job_skills`, `student_skills`, `jobs` |
| **Grain** | Student × Job |
| **Computed** | At search query time (not stored) |

**Decision**: Which jobs to surface to a student. Jobs below `skill_threshold` are filtered out of the main results and shown greyed-out. Founder can adjust weights and threshold per job to change market dynamics.

---

### 9. Skill Threshold Gate
| Field | Value |
|---|---|
| **Definition** | Binary gate: if `fit_score >= jobs.skill_threshold`, the student "passes" and the job is shown prominently |
| **SQL** | `CASE WHEN fit_score >= skill_threshold THEN 'above' ELSE 'below'` |
| **Source** | Computed from fit score and `jobs.skill_threshold` |
| **Threshold range** | 50–80 (set per job by company) |

**What happens when a student doesn't meet the threshold?** They can still see the job, but it appears below all threshold-passing results, greyed out, and marked "Below Threshold". They are NOT shown to the company in the candidate list unless the company explicitly searches below-threshold applicants.

**Decision**: Too strict (threshold 80+) → few matches, companies can't hire. Too lenient (threshold 50) → companies get poor-fit applications. Target: view-to-apply rate 10–25%, shortlist rate 20–40%.

---

## Conversion Metrics

### 10. View → Apply Rate
| Field | Value |
|---|---|
| **Definition** | Percentage of job views that result in an application |
| **SQL** | `COUNT(application_submitted events) / COUNT(student_viewed_job events) × 100` |
| **Source Tables** | `events` |
| **Window** | Rolling 30 days |
| **Healthy range** | 5–30% |

**Decision**: Quality of job-page UX. < 5% → job description is weak, or skill threshold is blocking too many students. > 30% → threshold may be too low (students are applying to everything).

---

### 11. Student Engagement Rate
| Field | Value |
|---|---|
| **Definition** | % of active students who searched at least once in the last 7 days |
| **SQL** | `COUNT(DISTINCT sl.student_id) / COUNT(DISTINCT students) × 100 WHERE searched_at >= '-7 days'` |
| **Source Tables** | `search_logs`, `students` |
| **Window** | Rolling 7 days |

**Decision**: Platform stickiness. < 30% → students signed up but aren't returning. Trigger re-engagement campaigns.

---

## Data Quality Metrics

### 12. Event Freshness (1h)
| Field | Value |
|---|---|
| **Definition** | Count of events ingested in the last 60 minutes |
| **SQL** | `SELECT COUNT(*) FROM events WHERE ingested_at >= datetime('now','-1 hour')` |
| **Check type** | Freshness |
| **FAIL threshold** | 0 events (no events = broken pipeline) |

**Decision**: Is the pipeline alive? FAIL → alert the engineer on call. This check runs on every dashboard page load.

---

### 13. Null job_id on View/Apply
| Field | Value |
|---|---|
| **Definition** | Count of view/apply events where job_id is NULL |
| **SQL** | `SELECT COUNT(*) FROM events WHERE event_type IN ('student_viewed_job','application_submitted') AND job_id IS NULL` |
| **Check type** | Null check |
| **WARN threshold** | > 0 |

**Decision**: Data completeness. Any nulls mean the event emitter isn't attaching job context → these events can't be used in funnel analysis.

---

### 14. Duplicate Applications
| Field | Value |
|---|---|
| **Definition** | Count of (student_id, job_id) pairs with more than one application |
| **SQL** | `SELECT COUNT(*) FROM (SELECT student_id, job_id FROM applications GROUP BY student_id, job_id HAVING COUNT(*) > 1)` |
| **Check type** | Duplicate |
| **WARN threshold** | > 0 |

**Decision**: Application integrity. Duplicates inflate application counts and corrupt the funnel. Fix: add unique constraint at application creation.

---

### 15. Fit Score Range Sanity
| Field | Value |
|---|---|
| **Definition** | Count of applications where fit_score is outside [0,100] |
| **SQL** | `SELECT COUNT(*) FROM applications WHERE fit_score < 0 OR fit_score > 100` |
| **Check type** | Sanity |
| **FAIL threshold** | > 0 |

**Decision**: Calculation bug. Any out-of-range scores mean the fit formula has an error — investigate the skill-match computation immediately.

---

## Glossary

| Term | Definition |
|---|---|
| **Event** | A structured log entry in the `events` table, emitted when something happens on the platform |
| **Metric** | A number derived from events by aggregation (count, sum, average, ratio) |
| **KPI** | A metric tied directly to a business decision or health indicator |
| **Vanity metric** | A number that looks good but doesn't inform any decision — excluded from this dashboard |
| **Skill Threshold** | The minimum fit score (0–100) required for a student to appear in a company's candidate list for a job |
| **Fit Score** | A weighted score combining skill match (70%) and job recency (30%), computed per student×job pair |
| **DPDP** | India's Digital Personal Data Protection Act — events must not store PII beyond what is consented to |
