"""
PlaceMux · Company Funnel Analytics
api/server.py — Lightweight HTTP API server (stdlib only, no pip needed)

Endpoints:
  GET /api/funnel          → Overall company funnel stages + daily trend
  GET /api/companies       → Per-company funnel leaderboard
  GET /api/search          → Job search with fit scoring (?q=&student_id=)
  GET /api/quality         → Data quality check results
  GET /api/metrics         → High-level KPI summary
  GET /api/trends          → 30-day daily trend data
  GET /api/skills          → All skills (for search autocomplete)
  GET /api/students        → Student list (for demo student switcher)

Run: python api/server.py
"""

import json
import sqlite3
import sys
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# ─── Config ───────────────────────────────────────────────
PORT = 8765
DB_PATH = Path(__file__).parent.parent / "placemux.db"
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
}

# ─── DB Helper ────────────────────────────────────────────
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA query_only=ON")
    return conn

def rows_to_list(rows):
    return [dict(r) for r in rows]


def get_funnel_stages():
    conn = get_conn()
    row = conn.execute("""
        WITH
        s1 AS (SELECT COUNT(DISTINCT actor_id) n FROM events WHERE event_type='company_signed_up' AND occurred_at>=datetime('now','-30 days')),
        s2 AS (SELECT COUNT(DISTINCT company_id) n FROM events WHERE event_type='company_posted_job' AND occurred_at>=datetime('now','-30 days')),
        s3 AS (SELECT COUNT(DISTINCT student_id) n FROM events WHERE event_type='student_signed_up' AND occurred_at>=datetime('now','-30 days')),
        s4 AS (SELECT COUNT(DISTINCT student_id) n FROM events WHERE event_type='student_searched_jobs' AND occurred_at>=datetime('now','-30 days')),
        s5 AS (SELECT COUNT(DISTINCT job_id) n FROM events WHERE event_type='student_viewed_job' AND occurred_at>=datetime('now','-30 days')),
        s6 AS (SELECT COUNT(*) n FROM events WHERE event_type='application_submitted' AND occurred_at>=datetime('now','-30 days')),
        s7 AS (SELECT COUNT(*) n FROM events WHERE event_type='company_shortlisted' AND occurred_at>=datetime('now','-30 days'))
        SELECT
            (SELECT n FROM s1) AS companies_signed_up,
            (SELECT n FROM s2) AS companies_posted_job,
            (SELECT n FROM s3) AS students_signed_up,
            (SELECT n FROM s4) AS students_searched,
            (SELECT n FROM s5) AS jobs_viewed_unique,
            (SELECT n FROM s6) AS applications_submitted,
            (SELECT n FROM s7) AS candidates_shortlisted
    """).fetchone()
    conn.close()

    data = dict(row)
    stages = [
        {"stage": "Companies Signed Up",    "key": "companies_signed_up",    "count": data["companies_signed_up"],    "color": "#6C63FF"},
        {"stage": "Companies Posted Job",   "key": "companies_posted_job",   "count": data["companies_posted_job"],   "color": "#4ECDC4"},
        {"stage": "Students Signed Up",     "key": "students_signed_up",     "count": data["students_signed_up"],     "color": "#45B7D1"},
        {"stage": "Students Searched",      "key": "students_searched",      "count": data["students_searched"],      "color": "#96CEB4"},
        {"stage": "Jobs Viewed (Unique)",   "key": "jobs_viewed_unique",     "count": data["jobs_viewed_unique"],     "color": "#FFEAA7"},
        {"stage": "Applications Submitted", "key": "applications_submitted", "count": data["applications_submitted"], "color": "#FD79A8"},
        {"stage": "Candidates Shortlisted", "key": "candidates_shortlisted", "count": data["candidates_shortlisted"], "color": "#00B894"},
    ]
    for i in range(1, len(stages)):
        prev = stages[i-1]["count"]
        curr = stages[i]["count"]
        stages[i]["conversion_pct"] = round(curr * 100 / prev, 1) if prev > 0 else 0

    return {"stages": stages, "window_days": 30}

def get_metrics():
    conn = get_conn()
    row = conn.execute("""
        SELECT
            (SELECT COUNT(*) FROM companies WHERE is_active=1) AS total_companies,
            (SELECT COUNT(*) FROM students WHERE is_active=1) AS total_students,
            (SELECT COUNT(*) FROM jobs WHERE is_active=1) AS active_jobs,
            (SELECT COUNT(*) FROM applications) AS total_applications,
            (SELECT COUNT(*) FROM applications WHERE status='shortlisted') AS total_shortlisted,
            (SELECT ROUND(AVG(fit_score),1) FROM applications) AS avg_fit_score,
            (SELECT COUNT(*) FROM search_logs WHERE searched_at >= datetime('now','-24 hours')) AS searches_today,
            (SELECT COUNT(*) FROM events WHERE event_type='application_submitted' AND occurred_at>=datetime('now','-24 hours')) AS applications_today,
            (SELECT COUNT(*) FROM events WHERE event_type='company_posted_job' AND occurred_at>=datetime('now','-7 days')) AS jobs_posted_7d,
            (SELECT ROUND(COUNT(DISTINCT sl.student_id)*100.0/NULLIF((SELECT COUNT(*) FROM students WHERE is_active=1),0),1) FROM search_logs sl WHERE sl.searched_at >= datetime('now','-7 days')) AS student_engagement_rate,
            (SELECT ROUND(COUNT(*)*100.0/NULLIF((SELECT COUNT(*) FROM events WHERE event_type='student_viewed_job'),0),1) FROM events WHERE event_type='application_submitted') AS view_to_apply_pct,
            (SELECT MAX(ingested_at) FROM events) AS last_event_at
    """).fetchone()
    conn.close()
    return dict(row)

def get_trends():
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            DATE(occurred_at) AS event_date,
            SUM(CASE WHEN event_type='company_posted_job' THEN 1 ELSE 0 END) AS jobs_posted,
            SUM(CASE WHEN event_type='student_searched_jobs' THEN 1 ELSE 0 END) AS searches,
            SUM(CASE WHEN event_type='student_viewed_job' THEN 1 ELSE 0 END) AS job_views,
            SUM(CASE WHEN event_type='application_submitted' THEN 1 ELSE 0 END) AS applications,
            SUM(CASE WHEN event_type='company_shortlisted' THEN 1 ELSE 0 END) AS shortlisted,
            COUNT(DISTINCT CASE WHEN event_type='student_searched_jobs' THEN actor_id END) AS active_students,
            COUNT(DISTINCT CASE WHEN event_type='company_posted_job' THEN actor_id END) AS active_companies
        FROM events
        WHERE occurred_at >= datetime('now', '-30 days')
        GROUP BY DATE(occurred_at)
        ORDER BY event_date
    """).fetchall()
    conn.close()
    return {"trend": rows_to_list(rows)}

def get_companies():
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            c.company_id, c.name AS company_name, c.industry, c.size, c.location,
            COUNT(DISTINCT CASE WHEN e.event_type='company_posted_job' AND e.occurred_at>=datetime('now','-30 days') THEN e.job_id END) AS jobs_posted,
            COUNT(DISTINCT CASE WHEN e.event_type='student_viewed_job' AND e.occurred_at>=datetime('now','-30 days') THEN e.student_id END) AS unique_viewers,
            COUNT(CASE WHEN e.event_type='student_viewed_job' AND e.occurred_at>=datetime('now','-30 days') THEN 1 END) AS total_views,
            COUNT(CASE WHEN e.event_type='application_submitted' AND e.occurred_at>=datetime('now','-30 days') THEN 1 END) AS applications_received,
            COUNT(CASE WHEN e.event_type='company_shortlisted' AND e.occurred_at>=datetime('now','-30 days') THEN 1 END) AS shortlisted,
            ROUND(AVG(CASE WHEN e.event_type='application_submitted' THEN CAST(json_extract(e.properties,'$.fit_score') AS REAL) END),1) AS avg_fit_score,
            CASE WHEN COUNT(CASE WHEN e.event_type='student_viewed_job' THEN 1 END)=0 THEN 0
                 ELSE ROUND(COUNT(CASE WHEN e.event_type='application_submitted' THEN 1 END)*100.0/COUNT(CASE WHEN e.event_type='student_viewed_job' THEN 1 END),1)
            END AS view_to_apply_pct
        FROM companies c
        LEFT JOIN events e ON e.company_id=c.company_id
        GROUP BY c.company_id, c.name, c.industry, c.size, c.location
        HAVING jobs_posted > 0
        ORDER BY applications_received DESC
        LIMIT 20
    """).fetchall()
    conn.close()
    return {"companies": rows_to_list(rows)}

def get_search(query="", student_id=None):
    conn = get_conn()

    # Default to first student for demo if none provided
    if not student_id:
        row = conn.execute("SELECT student_id FROM students WHERE is_active=1 LIMIT 1").fetchone()
        student_id = row[0] if row else None

    if not student_id:
        conn.close()
        return {"results": [], "student_id": None, "query": query}

    # Get student skills
    student_skills = conn.execute("""
        SELECT ss.skill_id, ss.proficiency, s.skill_name
        FROM student_skills ss JOIN skills s ON s.skill_id=ss.skill_id
        WHERE ss.student_id=?
    """, (student_id,)).fetchall()

    student_skill_map = {r["skill_id"]: r["proficiency"] for r in student_skills}
    student_skill_names = {r["skill_id"]: r["skill_name"] for r in student_skills}

    # Get all active jobs with their skills
    jobs = conn.execute("""
        SELECT j.job_id, j.company_id, j.title, j.job_type, j.location,
               j.salary_min, j.salary_max, j.skill_threshold, j.posted_at,
               c.name AS company_name, c.industry,
               (julianday('now') - julianday(j.posted_at)) AS days_ago
        FROM jobs j JOIN companies c ON c.company_id=j.company_id
        WHERE j.is_active=1
        ORDER BY j.posted_at DESC
    """).fetchall()

    results = []
    for job in jobs:
        job = dict(job)
        job_skills = conn.execute("""
            SELECT js.skill_id, js.weight, js.is_mandatory, s.skill_name
            FROM job_skills js JOIN skills s ON s.skill_id=js.skill_id
            WHERE js.job_id=?
        """, (job["job_id"],)).fetchall()

        total_weight = sum(r["weight"] for r in job_skills) or 1
        matched_weight = 0.0
        matched_skill_names = []

        for js in job_skills:
            sid = js["skill_id"]
            if sid in student_skill_map:
                prof = student_skill_map[sid]
                matched_weight += js["weight"] * (prof / 5.0)
                matched_skill_names.append(js["skill_name"])
            elif js["is_mandatory"]:
                matched_weight -= js["weight"] * 0.5

        skill_score = max(0, min(100, (matched_weight / total_weight) * 100))
        recency_score = max(0, min(1.0, 1.0 - job["days_ago"] / 30.0))
        fit_score = round(skill_score * 0.70 + recency_score * 100 * 0.30, 1)
        fit_score = max(0, min(100, fit_score))
        meets_threshold = fit_score >= job["skill_threshold"]

        # Collect all skill names for keyword search (not just matched)
        all_skill_names = [js["skill_name"] for js in job_skills]

        # Keyword filter — search title, company, industry, AND all required skills
        q = query.lower()
        if q and q not in job["title"].lower() and q not in job["company_name"].lower() \
                and q not in job["industry"].lower() \
                and not any(q in sk.lower() for sk in all_skill_names):
            continue

        results.append({
            **job,
            "skill_score": round(skill_score, 1),
            "recency_score": round(recency_score, 3),
            "fit_score": fit_score,
            "required_skill_count": len(job_skills),
            "matched_skill_count": len(matched_skill_names),
            "matched_skills": matched_skill_names,
            "meets_threshold": meets_threshold,
        })

    # Sort: threshold passers first, then by fit score
    results.sort(key=lambda x: (0 if x["meets_threshold"] else 1, -x["fit_score"]))
    results = results[:50]

    # Get student info
    stu = conn.execute("""
        SELECT s.student_id, s.name, s.college, s.degree,
               GROUP_CONCAT(sk.skill_name, ', ') AS skills
        FROM students s
        LEFT JOIN student_skills ss ON ss.student_id=s.student_id
        LEFT JOIN skills sk ON sk.skill_id=ss.skill_id
        WHERE s.student_id=?
        GROUP BY s.student_id
    """, (student_id,)).fetchone()

    conn.close()
    return {
        "results": results,
        "student": dict(stu) if stu else None,
        "query": query,
        "total_results": len(results),
    }

def get_quality():
    conn = get_conn()

    checks = []

    # 1. Freshness
    recent = conn.execute(
        "SELECT COUNT(*) FROM events WHERE ingested_at >= datetime('now','-1 hour')"
    ).fetchone()[0]
    last_event = conn.execute("SELECT MAX(ingested_at) FROM events").fetchone()[0]
    checks.append({
        "check_name": "Event Freshness (1h)", "check_type": "freshness",
        "value": recent, "threshold": 1, "unit": "events",
        "status": "pass" if recent >= 1 else "fail",
        "details": f"{recent} events in last 60 min. Last: {last_event}"
    })

    # 2. Null job_id on view/apply
    null_j = conn.execute(
        "SELECT COUNT(*) FROM events WHERE event_type IN ('student_viewed_job','application_submitted') AND job_id IS NULL"
    ).fetchone()[0]
    checks.append({
        "check_name": "Null job_id on View/Apply", "check_type": "null_check",
        "value": null_j, "threshold": 0, "unit": "events",
        "status": "pass" if null_j == 0 else ("warn" if null_j < 10 else "fail"),
        "details": f"{null_j} view/apply events are missing job_id"
    })

    # 3. Duplicate applications
    dupes = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT student_id, job_id FROM applications
            GROUP BY student_id, job_id HAVING COUNT(*)>1
        )
    """).fetchone()[0]
    checks.append({
        "check_name": "Duplicate Applications", "check_type": "duplicate",
        "value": dupes, "threshold": 0, "unit": "pairs",
        "status": "pass" if dupes == 0 else "warn",
        "details": f"{dupes} student+job pairs have >1 application"
    })

    # 4. Fit score range
    oor = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE fit_score<0 OR fit_score>100"
    ).fetchone()[0]
    checks.append({
        "check_name": "Fit Score Range [0,100]", "check_type": "sanity",
        "value": oor, "threshold": 0, "unit": "violations",
        "status": "pass" if oor == 0 else "fail",
        "details": f"{oor} applications with fit_score outside valid range"
    })

    # 5. Jobs missing skills
    no_sk = conn.execute("""
        SELECT COUNT(*) FROM jobs j WHERE is_active=1
        AND NOT EXISTS(SELECT 1 FROM job_skills WHERE job_id=j.job_id)
    """).fetchone()[0]
    checks.append({
        "check_name": "Jobs Missing Skills", "check_type": "sanity",
        "value": no_sk, "threshold": 0, "unit": "jobs",
        "status": "pass" if no_sk == 0 else ("warn" if no_sk < 5 else "fail"),
        "details": f"{no_sk} active jobs have no required skills defined"
    })

    # 6. Zero-result search rate (last 24h)
    sl_row = conn.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN results_count=0 THEN 1 ELSE 0 END) AS zero_results
        FROM search_logs WHERE searched_at>=datetime('now','-24 hours')
    """).fetchone()
    total_sl = sl_row[0] or 1
    zero_pct = round(sl_row[1] * 100 / total_sl, 1)
    checks.append({
        "check_name": "Zero-Result Search Rate (24h)", "check_type": "sanity",
        "value": zero_pct, "threshold": 30, "unit": "%",
        "status": "pass" if zero_pct < 30 else ("warn" if zero_pct < 50 else "fail"),
        "details": f"{zero_pct}% of searches in last 24h returned 0 results"
    })

    # 7. Event↔Table consistency
    ev_apps = conn.execute("SELECT COUNT(*) FROM events WHERE event_type='application_submitted'").fetchone()[0]
    tbl_apps = conn.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    discrepancy_pct = round(abs(ev_apps - tbl_apps) * 100 / max(tbl_apps, 1), 1)
    checks.append({
        "check_name": "Event↔Table Consistency", "check_type": "sanity",
        "value": discrepancy_pct, "threshold": 5, "unit": "%",
        "status": "pass" if discrepancy_pct <= 5 else "warn",
        "details": f"Events: {ev_apps}, Table: {tbl_apps}, Discrepancy: {discrepancy_pct}%"
    })

    conn.close()
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {
        "checks": checks,
        "summary": {"total": len(checks), "passed": passed, "warned": sum(1 for c in checks if c["status"]=="warn"), "failed": sum(1 for c in checks if c["status"]=="fail")},
        "checked_at": datetime.now(timezone.utc).isoformat()
    }

def get_skills():
    conn = get_conn()
    rows = conn.execute("SELECT skill_id, skill_name, category FROM skills ORDER BY skill_name").fetchall()
    conn.close()
    return {"skills": rows_to_list(rows)}

def get_students():
    conn = get_conn()
    rows = conn.execute("""
        SELECT s.student_id, s.name, s.college, s.degree, s.graduation_year,
               GROUP_CONCAT(sk.skill_name, ', ') AS skills
        FROM students s
        LEFT JOIN student_skills ss ON ss.student_id=s.student_id
        LEFT JOIN skills sk ON sk.skill_id=ss.skill_id
        WHERE s.is_active=1
        GROUP BY s.student_id
        ORDER BY s.name
        LIMIT 30
    """).fetchall()
    conn.close()
    return {"students": rows_to_list(rows)}

# ─── HTTP Handler ─────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence default logging

    def send_json(self, data, status=200):
        body = json.dumps(data, default=str).encode()
        self.send_response(status)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        qs = parse_qs(parsed.query)

        try:
            if path == "/api/funnel":
                self.send_json(get_funnel_stages())
            elif path == "/api/metrics":
                self.send_json(get_metrics())
            elif path == "/api/trends":
                self.send_json(get_trends())
            elif path == "/api/companies":
                self.send_json(get_companies())
            elif path == "/api/search":
                q = qs.get("q", [""])[0]
                sid = qs.get("student_id", [None])[0]
                self.send_json(get_search(q, sid))
            elif path == "/api/quality":
                self.send_json(get_quality())
            elif path == "/api/skills":
                self.send_json(get_skills())
            elif path == "/api/students":
                self.send_json(get_students())
            elif path == "/health":
                self.send_json({"status": "ok", "db": str(DB_PATH), "db_exists": DB_PATH.exists()})
            else:
                self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)
            import traceback; traceback.print_exc()

# ─── Main ─────────────────────────────────────────────────
if __name__ == "__main__":
    if not DB_PATH.exists():
        print(f"❌  Database not found at {DB_PATH}")
        print("    Run: python seed_data.py  first")
        sys.exit(1)

    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"✅  PlaceMux API running at http://localhost:{PORT}")
    print(f"    Database: {DB_PATH}")
    print(f"    Endpoints: /api/funnel  /api/metrics  /api/trends")
    print(f"               /api/companies  /api/search  /api/quality")
    print(f"               /api/skills  /api/students  /health")
    print("    Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹  Server stopped.")
