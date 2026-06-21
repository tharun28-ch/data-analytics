#!/bin/bash
# ============================================================
# PlaceMux · Company Funnel · Demo Launch Script
# run_demo.sh — One command: seed → serve → open dashboard
#
# Usage:  bash run_demo.sh
# ============================================================

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PURPLE='\033[0;35m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${PURPLE}${BOLD}════════════════════════════════════════════════${RESET}"
echo -e "${PURPLE}${BOLD}  PlaceMux · Company Funnel Analytics · Demo    ${RESET}"
echo -e "${PURPLE}${BOLD}  Task 3 · Phase 2 · Altrodav Technologies       ${RESET}"
echo -e "${PURPLE}${BOLD}════════════════════════════════════════════════${RESET}"
echo ""

# ── Step 1: Check Python ────────────────────────────────────
echo -e "${CYAN}[1/4] Checking Python...${RESET}"
if ! command -v python3 &>/dev/null; then
    echo -e "${YELLOW}⚠ python3 not found, trying python...${RESET}"
    if ! command -v python &>/dev/null; then
        echo "❌  Python not found. Please install Python 3.8+"
        exit 1
    fi
    PYTHON=python
else
    PYTHON=python3
fi
echo -e "${GREEN}✓ Python: $($PYTHON --version)${RESET}"

# ── Step 2: Seed the database ──────────────────────────────
echo ""
echo -e "${CYAN}[2/4] Seeding database with realistic sample data...${RESET}"
if [ -f "placemux.db" ]; then
    echo -e "${YELLOW}  ↻ Existing database found — re-seeding...${RESET}"
fi
$PYTHON seed_data.py
echo -e "${GREEN}✓ Database seeded: placemux.db${RESET}"

# ── Step 3: Verify data ─────────────────────────────────────
echo ""
echo -e "${CYAN}[3/4] Verifying data integrity...${RESET}"
$PYTHON -c "
import sqlite3
conn = sqlite3.connect('placemux.db')
checks = {
    'companies':     conn.execute('SELECT COUNT(*) FROM companies').fetchone()[0],
    'students':      conn.execute('SELECT COUNT(*) FROM students').fetchone()[0],
    'jobs':          conn.execute('SELECT COUNT(*) FROM jobs').fetchone()[0],
    'events':        conn.execute('SELECT COUNT(*) FROM events').fetchone()[0],
    'applications':  conn.execute('SELECT COUNT(*) FROM applications').fetchone()[0],
    'search_logs':   conn.execute('SELECT COUNT(*) FROM search_logs').fetchone()[0],
}
print('  Row counts:')
for k,v in checks.items():
    ok = '✓' if v > 0 else '✗'
    print(f'    {ok}  {k:<20} {v:>6}')
assert all(v > 0 for v in checks.values()), 'Some tables are empty!'

# Quick funnel check
funnel = conn.execute('''
    SELECT
        SUM(CASE WHEN event_type=\"application_submitted\" THEN 1 ELSE 0 END) apps,
        SUM(CASE WHEN event_type=\"student_searched_jobs\" THEN 1 ELSE 0 END) searches
    FROM events
''').fetchone()
print(f'  Funnel: {funnel[1]} searches → {funnel[0]} applications ✓')
conn.close()
print('  All integrity checks passed!')
"
echo -e "${GREEN}✓ Data verified${RESET}"

# ── Step 4: Start API server + open dashboard ───────────────
echo ""
echo -e "${CYAN}[4/4] Starting API server...${RESET}"
echo ""
echo -e "${PURPLE}${BOLD}  Dashboard: ${CYAN}file://$(pwd)/dashboard/index.html${RESET}"
echo -e "${PURPLE}${BOLD}  API Base:  ${CYAN}http://localhost:8765${RESET}"
echo ""
echo -e "${YELLOW}  API Endpoints:${RESET}"
echo -e "    /api/funnel      → Company funnel stages"
echo -e "    /api/metrics     → KPI summary"
echo -e "    /api/trends      → 30-day daily trend"
echo -e "    /api/companies   → Per-company leaderboard"
echo -e "    /api/search      → Job search with fit ranking"
echo -e "    /api/quality     → Data quality checks"
echo -e "    /health          → Server health check"
echo ""
echo -e "${YELLOW}  2-Minute Demo Script:${RESET}"
echo -e "    1. Open dashboard → all KPI cards show real numbers"
echo -e "    2. Funnel tab → explain each stage + conversion rate"
echo -e "    3. Search tab → select student → type 'Python' → ranked results appear"
echo -e "    4. Quality tab → 7 checks, all green"
echo -e "    5. Metrics tab → explain each number's source"
echo ""
echo -e "${GREEN}${BOLD}  Press Ctrl+C to stop the server${RESET}"
echo ""

# Open dashboard in browser
sleep 1
if command -v open &>/dev/null; then
    open "dashboard/index.html"
elif command -v xdg-open &>/dev/null; then
    xdg-open "dashboard/index.html"
fi

# Start API server (foreground)
$PYTHON api/server.py
