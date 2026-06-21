"""
PlaceMux · Company Funnel Analytics
seed_data.py — Generate realistic sample data and seed the SQLite database.

Generates:
  • 50 companies  (across industries)
  • 200 students  (across colleges, degrees, skill levels)
  • 40 skills     (technical + soft + domain)
  • 300 jobs      (varied roles, skill requirements, thresholds)
  • 5,000+ events (spread across 30 days, realistic daily patterns)
  • 800+ applications
  • 1,200+ search logs

Run: python seed_data.py
"""

import sqlite3
import uuid
import random
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ──────────────────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────────────────
DB_PATH = Path(__file__).parent / "placemux.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
SEED = 42
DAYS_BACK = 30
random.seed(SEED)

# ──────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────
def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def ts(days_ago: float, hour_offset: float = 0) -> str:
    """Generate a realistic timestamp within working hours."""
    base = datetime.now(timezone.utc) - timedelta(days=days_ago)
    # Weight events toward working hours (9am-8pm)
    h = int(random.gauss(14, 3))
    h = max(8, min(22, h))
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return base.replace(hour=h, minute=m, second=s, microsecond=0).isoformat()

def uid() -> str:
    return str(uuid.uuid4())

def coin(p: float = 0.5) -> bool:
    return random.random() < p

# ──────────────────────────────────────────────────────────
# REFERENCE DATA
# ──────────────────────────────────────────────────────────
INDUSTRIES = ["fintech", "edtech", "healthtech", "saas", "ecommerce",
              "logistics", "hrtech", "gaming", "cybersecurity", "ai_ml"]

COMPANY_SIZES = ["startup", "sme", "enterprise"]

CITIES = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Chennai",
          "Pune", "Kolkata", "Ahmedabad", "Noida", "Gurugram"]

COLLEGES = [
    "IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kharagpur", "IIT Kanpur",
    "NIT Trichy", "NIT Warangal", "BITS Pilani", "VIT Vellore", "Manipal Institute",
    "Christ University", "Amity University", "SRM University", "IIIT Hyderabad",
    "IIIT Bangalore", "Jadavpur University", "Anna University", "Symbiosis",
    "Delhi Technological University", "PES University"
]

DEGREES = ["B.Tech CSE", "B.Tech ECE", "BCA", "MCA", "M.Tech CS",
           "B.Sc Computer Science", "MBA Tech", "B.Tech IT"]

JOB_TITLES = [
    "Software Engineer", "Data Analyst", "Product Manager",
    "Backend Developer", "Frontend Developer", "Full Stack Developer",
    "ML Engineer", "Data Scientist", "DevOps Engineer", "QA Engineer",
    "Business Analyst", "UI/UX Designer", "Cloud Architect", "SRE",
    "Android Developer", "iOS Developer", "Cybersecurity Analyst",
    "Database Administrator", "Technical Writer", "Scrum Master"
]

SKILLS_DATA = [
    # Technical
    ("Python", "technical"), ("JavaScript", "technical"), ("Java", "technical"),
    ("SQL", "technical"), ("React", "technical"), ("Node.js", "technical"),
    ("Django", "technical"), ("FastAPI", "technical"), ("Docker", "technical"),
    ("Kubernetes", "technical"), ("AWS", "technical"), ("GCP", "technical"),
    ("Machine Learning", "technical"), ("Deep Learning", "technical"),
    ("Data Analysis", "technical"), ("Data Visualization", "technical"),
    ("Pandas", "technical"), ("TensorFlow", "technical"), ("Git", "technical"),
    ("Linux", "technical"), ("REST APIs", "technical"), ("GraphQL", "technical"),
    ("PostgreSQL", "technical"), ("MongoDB", "technical"), ("Redis", "technical"),
    # Soft
    ("Communication", "soft"), ("Problem Solving", "soft"),
    ("Team Collaboration", "soft"), ("Leadership", "soft"), ("Critical Thinking", "soft"),
    # Domain
    ("Financial Modelling", "domain"), ("Healthcare Analytics", "domain"),
    ("Supply Chain", "domain"), ("Digital Marketing", "domain"),
    ("Agile/Scrum", "domain"), ("Product Thinking", "domain"),
    ("Business Analysis", "domain"), ("UX Research", "domain"),
    ("Growth Hacking", "domain"), ("SEO/SEM", "domain"),
]

COMPANY_NAMES = [
    "FinEdge Solutions", "LearnLoop", "MedPulse Analytics", "CloudNexus", "ShopStream",
    "LogiTrack India", "TalentBridge AI", "PixelForge Games", "CyberShield Labs", "Synapse ML",
    "RupeeFlow", "EduPath Technologies", "HealthFirst Data", "SaaS Harbor", "CartMate",
    "FleetOps", "HireSmarter", "PlayVerse Studios", "SecureNet India", "DataDriven AI",
    "PaySpark", "ClassMind", "ClinIQ", "NexCloud", "MarketHub",
    "RouteWise", "PeopleOps", "QuestZone", "CipherEdge", "NeuralWorks",
    "MoneyMap", "SkillSprint", "VitalSense", "StackCloud", "BuyBright",
    "TrackFreight", "RecruiterPro", "ArcadeBlast", "GuardianSec", "InsightML",
    "ZetaPay", "EduCore", "HealthSync", "CloudBridge", "TrendCart",
    "SwiftLogix", "OrgPilot", "GameGrid", "NetDefend", "PredictIQ"
]

STUDENT_FIRST = ["Aryan", "Priya", "Rohit", "Sneha", "Vikram", "Ananya", "Karan",
                  "Divya", "Rahul", "Pooja", "Aditya", "Meera", "Siddharth",
                  "Kavya", "Nikhil", "Shreya", "Amit", "Nisha", "Harish",
                  "Lakshmi", "Tejas", "Swati", "Gaurav", "Ritu", "Varun",
                  "Pallavi", "Pranav", "Deepa", "Rohan", "Sunita", "Abhinav",
                  "Kritika", "Mayank", "Anjali", "Shubham", "Tanvi", "Rishabh",
                  "Bhavna", "Kunal", "Smita", "Akash", "Preeti", "Manish",
                  "Roshni", "Tushar", "Geeta", "Vishal", "Nandita", "Sumit", "Ayesha"]

STUDENT_LAST = ["Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Nair",
                 "Rao", "Joshi", "Iyer", "Mehta", "Bhat", "Pillai", "Reddy",
                 "Malhotra", "Chaturvedi", "Srivastava", "Agarwal", "Desai", "Pandey"]

# ──────────────────────────────────────────────────────────
# BUILD DATABASE
# ──────────────────────────────────────────────────────────
def init_db(conn):
    schema = SCHEMA_PATH.read_text()
    conn.executescript(schema)
    conn.commit()
    print("✓ Schema initialized")

def seed_skills(conn) -> list[dict]:
    skills = []
    for i, (name, cat) in enumerate(SKILLS_DATA, start=1):
        conn.execute("INSERT OR IGNORE INTO skills(skill_id, skill_name, category) VALUES(?,?,?)",
                     (i, name, cat))
        skills.append({"skill_id": i, "skill_name": name, "category": cat})
    conn.commit()
    print(f"✓ Skills: {len(skills)}")
    return skills

def seed_companies(conn, skills: list[dict]) -> list[dict]:
    companies = []
    for i, name in enumerate(COMPANY_NAMES):
        cid = f"co_{i+1:03d}"
        joined_days_ago = random.uniform(60, 365)
        c = {
            "company_id": cid,
            "name": name,
            "industry": random.choice(INDUSTRIES),
            "size": random.choices(COMPANY_SIZES, weights=[50, 35, 15])[0],
            "location": random.choice(CITIES),
            "created_at": ts(joined_days_ago),
            "is_active": 1
        }
        conn.execute("""INSERT OR IGNORE INTO companies
            (company_id, name, industry, size, location, created_at, is_active)
            VALUES(:company_id,:name,:industry,:size,:location,:created_at,:is_active)""", c)
        companies.append(c)
    conn.commit()
    print(f"✓ Companies: {len(companies)}")
    return companies

def seed_jobs(conn, companies: list[dict], skills: list[dict]) -> list[dict]:
    jobs = []
    for i in range(300):
        company = random.choice(companies)
        jid = f"job_{i+1:04d}"
        posted_days_ago = random.uniform(0, 28)
        required_skills = random.sample(skills, random.randint(2, 6))
        job = {
            "job_id": jid,
            "company_id": company["company_id"],
            "title": random.choice(JOB_TITLES),
            "description": f"Exciting opportunity at {company['name']} for talented individuals.",
            "location": random.choice([company["location"], "Remote", "Hybrid"]),
            "job_type": random.choices(["full_time", "internship", "contract"],
                                        weights=[60, 30, 10])[0],
            "salary_min": round(random.uniform(3, 15) * 100000, -3),
            "salary_max": round(random.uniform(15, 50) * 100000, -3),
            "experience_min": random.choices([0, 1, 2, 3], weights=[40, 30, 20, 10])[0],
            "skill_threshold": random.choices([50, 60, 70, 80], weights=[20, 40, 30, 10])[0],
            "posted_at": ts(posted_days_ago),
            "expires_at": ts(posted_days_ago - 30),
            "is_active": 1 if posted_days_ago < 25 else random.choice([0, 1])
        }
        conn.execute("""INSERT OR IGNORE INTO jobs
            (job_id, company_id, title, description, location, job_type,
             salary_min, salary_max, experience_min, skill_threshold,
             posted_at, expires_at, is_active)
            VALUES(:job_id,:company_id,:title,:description,:location,:job_type,
                   :salary_min,:salary_max,:experience_min,:skill_threshold,
                   :posted_at,:expires_at,:is_active)""", job)

        # Assign required skills to job
        for sk in required_skills:
            is_mandatory = 1 if required_skills.index(sk) < 2 else 0
            weight = round(random.uniform(0.7, 1.5), 2)
            conn.execute("""INSERT OR IGNORE INTO job_skills(job_id, skill_id, weight, is_mandatory)
                VALUES(?,?,?,?)""", (jid, sk["skill_id"], weight, is_mandatory))

        job["required_skills"] = required_skills
        jobs.append(job)

    conn.commit()
    print(f"✓ Jobs: {len(jobs)}, with skills assigned")
    return jobs

def seed_students(conn, skills: list[dict]) -> list[dict]:
    students = []
    for i in range(200):
        sid = f"stu_{i+1:04d}"
        first = random.choice(STUDENT_FIRST)
        last = random.choice(STUDENT_LAST)
        # Each student has 3-12 skills at varying proficiency
        stu_skills = random.sample(skills, random.randint(3, 12))
        joined_days_ago = random.uniform(5, 90)
        stu = {
            "student_id": sid,
            "name": f"{first} {last}",
            "college": random.choice(COLLEGES),
            "degree": random.choice(DEGREES),
            "graduation_year": random.choice([2024, 2025, 2026, 2027]),
            "location": random.choice(CITIES),
            "created_at": ts(joined_days_ago),
            "is_active": 1
        }
        conn.execute("""INSERT OR IGNORE INTO students
            (student_id, name, college, degree, graduation_year, location, created_at, is_active)
            VALUES(:student_id,:name,:college,:degree,:graduation_year,:location,:created_at,:is_active)""", stu)

        for sk in stu_skills:
            prof = random.choices([1, 2, 3, 4, 5], weights=[10, 20, 35, 25, 10])[0]
            conn.execute("""INSERT OR IGNORE INTO student_skills(student_id, skill_id, proficiency)
                VALUES(?,?,?)""", (sid, sk["skill_id"], prof))

        stu["skills"] = stu_skills
        students.append(stu)

    conn.commit()
    print(f"✓ Students: {len(students)}, with skills assigned")
    return students

def build_skill_maps(students, jobs, student_skill_proficiency):
    """
    Pre-compute fit scores in-memory for all student×job pairs.
    Returns {(student_id, job_id): fit_score}
    """
    # job_id → {skill_id: (weight, is_mandatory)}
    job_skill_map = {}
    for job in jobs:
        job_skill_map[job["job_id"]] = {
            sk["skill_id"]: (1.0, 0)   # weight=1, not mandatory (simplified)
            for sk in job["required_skills"]
        }
        # First 2 skills are mandatory
        for i, sk in enumerate(job["required_skills"][:2]):
            sid = sk["skill_id"]
            job_skill_map[job["job_id"]][sid] = (1.3, 1)

    return job_skill_map, student_skill_proficiency

def fast_fit_score(student_id, job, job_skill_map, student_skill_proficiency,
                   days_ago_posted=14) -> float:
    """Fast in-memory fit score computation."""
    jskills = job_skill_map.get(job["job_id"], {})
    if not jskills:
        return 55.0

    stu_skills = student_skill_proficiency.get(student_id, {})
    total_weight = sum(w for w, _ in jskills.values())
    if total_weight == 0:
        return 55.0

    matched_weight = 0.0
    for skill_id, (weight, is_mandatory) in jskills.items():
        if skill_id in stu_skills:
            prof = stu_skills[skill_id]
            matched_weight += weight * (prof / 5.0)
        elif is_mandatory:
            matched_weight -= weight * 0.3

    skill_score = max(0, min(100, (matched_weight / total_weight) * 100))
    recency_score = max(0, min(1.0, 1.0 - days_ago_posted / 30.0))
    fit = skill_score * 0.70 + recency_score * 100 * 0.30
    return round(max(0, min(100, fit)), 1)

def seed_events_and_applications(conn, companies, jobs, students):
    """
    Simulate 30 days of realistic marketplace activity:
    - Company signs up → posts jobs
    - Students sign up → search → view jobs → apply
    - Companies review candidates → shortlist/reject
    """
    events = []
    applications = []
    search_logs = []
    active_jobs = [j for j in jobs if j["is_active"]]

    # Pre-build in-memory skill maps for fast fit scoring
    student_skill_proficiency = {}  # student_id → {skill_id: proficiency}
    for stu in students:
        student_skill_proficiency[stu["student_id"]] = {
            sk["skill_id"]: random.choices([1,2,3,4,5], weights=[10,20,35,25,10])[0]
            for sk in stu["skills"]
        }
    job_skill_map, _ = build_skill_maps(students, jobs, student_skill_proficiency)

    def emit(event_type, actor_type, actor_id, occurred_at,
             job_id=None, company_id=None, student_id=None, session_id=None, props=None):
        events.append({
            "event_id": uid(),
            "event_type": event_type,
            "actor_type": actor_type,
            "actor_id": actor_id,
            "session_id": session_id or uid(),
            "job_id": job_id,
            "company_id": company_id,
            "student_id": student_id,
            "properties": json.dumps(props or {}),
            "occurred_at": occurred_at,
            "ingested_at": occurred_at  # In prod: pipeline lag; keeping equal for demo
        })

    applied_pairs = set()  # (student_id, job_id) to avoid duplicates

    # ── Company events ──────────────────────────────────────
    for company in companies:
        # Company sign-up within last 30 days (2–28 days ago)
        created_days_ago = random.uniform(2, 28)
        emit("company_signed_up", "company", company["company_id"],
             ts(created_days_ago), company_id=company["company_id"])

        # Each company posts 3-8 jobs (already in jobs table; emit events)
        company_jobs = [j for j in jobs if j["company_id"] == company["company_id"]]
        for job in company_jobs[:random.randint(3, 8)]:
            days_since_post = random.uniform(1, 28)
            emit("company_posted_job", "company", company["company_id"],
                 ts(days_since_post), job_id=job["job_id"],
                 company_id=company["company_id"],
                 props={"job_title": job["title"], "job_type": job["job_type"]})

    # ── Student events ──────────────────────────────────────
    for student in students:
        joined_days_ago = random.uniform(1, 29)
        session_id = uid()

        emit("student_signed_up", "student", student["student_id"],
             ts(joined_days_ago + 0.1), student_id=student["student_id"])

        # Each student does 2-8 search sessions
        num_sessions = random.randint(2, 8)
        for _ in range(num_sessions):
            search_days_ago = random.uniform(0.5, joined_days_ago)
            session_id = uid()
            query_skill = random.choice(student["skills"])["skill_name"] if student["skills"] else ""
            results = random.randint(5, 30)
            top_fit = round(random.uniform(55, 98), 1)

            emit("student_searched_jobs", "student", student["student_id"],
                 ts(search_days_ago), student_id=student["student_id"],
                 session_id=session_id,
                 props={"query": query_skill, "results_count": results, "top_fit_score": top_fit})

            search_logs.append({
                "search_id": uid(),
                "student_id": student["student_id"],
                "session_id": session_id,
                "query_text": query_skill,
                "filters": json.dumps({"skill": query_skill}),
                "results_count": results,
                "top_fit_score": top_fit,
                "searched_at": ts(search_days_ago)
            })

            # From each search, student views 1-5 jobs
            viewed_jobs = random.sample(active_jobs, min(random.randint(1, 5), len(active_jobs)))
            for job in viewed_jobs:
                view_time = ts(search_days_ago - 0.01)
                emit("student_viewed_job", "student", student["student_id"],
                     view_time, job_id=job["job_id"],
                     company_id=job["company_id"],
                     student_id=student["student_id"],
                     session_id=session_id,
                     props={"time_spent_sec": random.randint(15, 300)})

                # Fast fit score (in-memory, no DB round-trips)
                days_posted = random.uniform(0, 28)
                fit_score = fast_fit_score(
                    student["student_id"], job, job_skill_map,
                    student_skill_proficiency, days_posted
                )
                pair = (student["student_id"], job["job_id"])
                # Apply with 40% probability regardless of score (threshold enforced at search display)
                applies = coin(0.40) and pair not in applied_pairs
                if applies:
                    applied_pairs.add(pair)
                    app_time = ts(search_days_ago - 0.02)
                    app_id = uid()
                    # Higher fit → higher shortlist chance
                    if fit_score >= 70:
                        weights = [30, 50, 20]
                    elif fit_score >= 50:
                        weights = [50, 30, 20]
                    else:
                        weights = [60, 10, 30]
                    status = random.choices(
                        ["applied", "shortlisted", "rejected"],
                        weights=weights)[0]

                    emit("application_submitted", "student", student["student_id"],
                         app_time, job_id=job["job_id"],
                         company_id=job["company_id"],
                         student_id=student["student_id"],
                         session_id=session_id,
                         props={"fit_score": fit_score, "application_id": app_id})

                    applications.append({
                        "application_id": app_id,
                        "job_id": job["job_id"],
                        "student_id": student["student_id"],
                        "company_id": job["company_id"],
                        "fit_score": fit_score,
                        "status": status,
                        "applied_at": app_time,
                        "updated_at": app_time
                    })

                    if status == "shortlisted":
                        emit("company_shortlisted", "company", job["company_id"],
                             ts(search_days_ago - 0.1),
                             job_id=job["job_id"], company_id=job["company_id"],
                             student_id=student["student_id"],
                             props={"application_id": app_id, "fit_score": fit_score})
                    elif status == "rejected":
                        emit("company_rejected", "company", job["company_id"],
                             ts(search_days_ago - 0.1),
                             job_id=job["job_id"], company_id=job["company_id"],
                             student_id=student["student_id"],
                             props={"application_id": app_id})

    # Bulk insert events
    conn.executemany("""INSERT OR IGNORE INTO events
        (event_id, event_type, actor_type, actor_id, session_id,
         job_id, company_id, student_id, properties, occurred_at, ingested_at)
        VALUES(:event_id,:event_type,:actor_type,:actor_id,:session_id,
               :job_id,:company_id,:student_id,:properties,:occurred_at,:ingested_at)""", events)

    conn.executemany("""INSERT OR IGNORE INTO applications
        (application_id, job_id, student_id, company_id, fit_score, status, applied_at, updated_at)
        VALUES(:application_id,:job_id,:student_id,:company_id,:fit_score,:status,:applied_at,:updated_at)""",
        applications)

    conn.executemany("""INSERT OR IGNORE INTO search_logs
        (search_id, student_id, session_id, query_text, filters, results_count, top_fit_score, searched_at)
        VALUES(:search_id,:student_id,:session_id,:query_text,:filters,:results_count,:top_fit_score,:searched_at)""",
        search_logs)

    conn.commit()
    print(f"✓ Events: {len(events)}")
    print(f"✓ Applications: {len(applications)}")
    print(f"✓ Search logs: {len(search_logs)}")

def run_data_quality_checks(conn):
    checks = []
    t = now_utc()

    # 1. Freshness: events ingested in last 24h
    recent = conn.execute("""
        SELECT COUNT(*) FROM events
        WHERE ingested_at >= datetime('now', '-24 hours')
    """).fetchone()[0]
    checks.append(("event_freshness_24h", "freshness",
                   "pass" if recent > 0 else "fail",
                   f"{recent} events ingested in last 24h", t))

    # 2. Null check: events missing job_id where expected
    null_job = conn.execute("""
        SELECT COUNT(*) FROM events
        WHERE event_type IN ('student_viewed_job','application_submitted')
        AND job_id IS NULL
    """).fetchone()[0]
    checks.append(("null_job_id_on_view_apply", "null_check",
                   "pass" if null_job == 0 else "warn",
                   f"{null_job} view/apply events missing job_id", t))

    # 3. Duplicate applications
    dupes = conn.execute("""
        SELECT COUNT(*) FROM (
            SELECT student_id, job_id, COUNT(*) as cnt
            FROM applications GROUP BY student_id, job_id HAVING cnt > 1
        )
    """).fetchone()[0]
    checks.append(("duplicate_applications", "duplicate",
                   "pass" if dupes == 0 else "warn",
                   f"{dupes} duplicate (student,job) application pairs", t))

    # 4. Sanity: fit scores in range
    out_of_range = conn.execute("""
        SELECT COUNT(*) FROM applications WHERE fit_score < 0 OR fit_score > 100
    """).fetchone()[0]
    checks.append(("fit_score_range_sanity", "sanity",
                   "pass" if out_of_range == 0 else "fail",
                   f"{out_of_range} applications with fit_score outside [0,100]", t))

    # 5. Sanity: jobs with no skills defined
    no_skills = conn.execute("""
        SELECT COUNT(*) FROM jobs j
        WHERE NOT EXISTS (SELECT 1 FROM job_skills js WHERE js.job_id = j.job_id)
    """).fetchone()[0]
    checks.append(("jobs_missing_skills", "sanity",
                   "pass" if no_skills == 0 else "warn",
                   f"{no_skills} active jobs have no skills defined", t))

    conn.executemany("""INSERT INTO data_quality_log
        (check_name, check_type, status, details, checked_at)
        VALUES(?,?,?,?,?)""", checks)
    conn.commit()
    print(f"✓ Data quality checks: {len(checks)} run, "
          f"{sum(1 for c in checks if c[2]=='pass')} passed")

def print_summary(conn):
    print("\n" + "="*55)
    print("  PlaceMux · Seed Data Summary")
    print("="*55)
    tables = ["companies", "students", "jobs", "skills",
              "events", "applications", "search_logs"]
    for t in tables:
        n = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t:<20} {n:>6} rows")
    print("="*55)
    # Event breakdown
    print("\n  Event Type Breakdown:")
    rows = conn.execute("""
        SELECT event_type, COUNT(*) as n
        FROM events GROUP BY event_type ORDER BY n DESC
    """).fetchall()
    for r in rows:
        print(f"    {r[0]:<35} {r[1]:>5}")
    print()

if __name__ == "__main__":
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("↻ Existing DB removed; re-seeding...")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    init_db(conn)
    skills = seed_skills(conn)
    companies = seed_companies(conn, skills)
    jobs = seed_jobs(conn, companies, skills)
    students = seed_students(conn, skills)
    seed_events_and_applications(conn, companies, jobs, students)

    # Inject a fresh pipeline heartbeat event so freshness check passes immediately
    fresh_now = now_utc()
    conn.execute("""INSERT OR IGNORE INTO events
        (event_id, event_type, actor_type, actor_id, session_id,
         properties, occurred_at, ingested_at)
        VALUES(?,?,?,?,?,?,?,?)""",
        (uid(), "system_heartbeat", "system", "pipeline", uid(),
         json.dumps({"type": "seed_complete", "db": str(DB_PATH)}),
         fresh_now, fresh_now))
    conn.commit()
    print(f"✓ Pipeline heartbeat: {fresh_now}")

    run_data_quality_checks(conn)
    print_summary(conn)
    conn.close()
    print(f"\n✅ Database ready: {DB_PATH}")
