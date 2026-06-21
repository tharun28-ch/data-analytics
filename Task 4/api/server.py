import json
import sqlite3
import sys
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

# ─── Config ───────────────────────────────────────────────
PORT = 8766
DB_PATH = Path(__file__).parent.parent / "placemux.db"
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
    "Cache-Control": "no-cache",
}

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA query_only=ON")
    return conn

def rows_to_list(rows):
    return [dict(r) for r in rows]

def get_application_funnel():
    conn = get_conn()
    row = conn.execute("""
        WITH
        s1 AS (SELECT COUNT(*) n FROM events WHERE event_type='student_viewed_job'),
        s2 AS (SELECT COUNT(*) n FROM events WHERE event_type='application_submitted'),
        s3 AS (SELECT COUNT(*) n FROM events WHERE event_type='company_shortlisted'),
        s4 AS (SELECT COUNT(*) n FROM events WHERE event_type='company_rejected')
        SELECT
            (SELECT n FROM s1) AS jobs_viewed,
            (SELECT n FROM s2) AS applications_submitted,
            (SELECT n FROM s3) AS candidates_shortlisted,
            (SELECT n FROM s4) AS candidates_rejected
    """).fetchone()
    conn.close()

    data = dict(row)
    stages = [
        {"stage": "Jobs Viewed",         "key": "jobs_viewed",            "count": data["jobs_viewed"],            "color": "#45B7D1"},
        {"stage": "Applications Submitted","key": "applications_submitted", "count": data["applications_submitted"], "color": "#96CEB4"},
        {"stage": "Shortlisted",         "key": "candidates_shortlisted", "count": data["candidates_shortlisted"], "color": "#00B894"}
    ]

    for i in range(1, len(stages)):
        prev = stages[i-1]["count"]
        curr = stages[i]["count"]
        stages[i]["conversion_pct"] = round(curr * 100 / prev, 1) if prev > 0 else 0

    return {
        "stages": stages,
        "rejected": data["candidates_rejected"],
        "total_applications": data["applications_submitted"]
    }

def get_application_quality():
    conn = get_conn()
    rows = conn.execute("""
        SELECT 
            CASE 
                WHEN a.fit_score >= j.skill_threshold THEN 'Meets Threshold'
                ELSE 'Below Threshold'
            END as category,
            COUNT(*) as total_applications,
            SUM(CASE WHEN a.status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted,
            SUM(CASE WHEN a.status = 'rejected' THEN 1 ELSE 0 END) as rejected,
            SUM(CASE WHEN a.status = 'applied' THEN 1 ELSE 0 END) as pending
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        GROUP BY category
    """).fetchall()
    conn.close()
    
    result = rows_to_list(rows)
    for r in result:
        total = r["total_applications"]
        r["shortlist_rate"] = round(r["shortlisted"] * 100 / total, 1) if total > 0 else 0
        r["rejection_rate"] = round(r["rejected"] * 100 / total, 1) if total > 0 else 0
        
    return {"quality_breakdown": result}

def get_trends():
    conn = get_conn()
    rows = conn.execute("""
        SELECT
            DATE(occurred_at) AS event_date,
            SUM(CASE WHEN event_type='application_submitted' THEN 1 ELSE 0 END) AS applications,
            SUM(CASE WHEN event_type='company_shortlisted' THEN 1 ELSE 0 END) AS shortlisted,
            SUM(CASE WHEN event_type='company_rejected' THEN 1 ELSE 0 END) AS rejected
        FROM events
        WHERE occurred_at >= datetime('now', '-30 days')
        GROUP BY DATE(occurred_at)
        ORDER BY event_date
    """).fetchall()
    conn.close()
    return {"trend": rows_to_list(rows)}

def get_quality():
    conn = get_conn()
    checks = []
    
    recent = conn.execute(
        "SELECT COUNT(*) FROM events WHERE ingested_at >= datetime('now','-1 hour')"
    ).fetchone()[0]
    checks.append({
        "check_name": "Event Freshness (1h)", "check_type": "freshness",
        "status": "pass" if recent >= 1 else "fail",
        "details": f"{recent} events in last 60 min."
    })
    
    null_apps = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE job_id IS NULL OR student_id IS NULL"
    ).fetchone()[0]
    checks.append({
        "check_name": "Null IDs in Applications", "check_type": "null_check",
        "status": "pass" if null_apps == 0 else "fail",
        "details": f"{null_apps} applications with null job or student ID"
    })
    
    conn.close()
    return {"checks": checks}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

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
        
        try:
            if path == "/api/funnel/applications":
                self.send_json(get_application_funnel())
            elif path == "/api/applications/quality":
                self.send_json(get_application_quality())
            elif path == "/api/trends":
                self.send_json(get_trends())
            elif path == "/api/quality":
                self.send_json(get_quality())
            elif path == "/health":
                self.send_json({"status": "ok"})
            else:
                self.send_json({"error": "Not found"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)
            import traceback; traceback.print_exc()

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"✅ PlaceMux API running at http://localhost:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("⏹ Server stopped.")
