const API_BASE = 'http://localhost:8766/api';

async function fetchData(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (err) {
        console.error(`Error fetching ${endpoint}:`, err);
        return null;
    }
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

async function renderKPIs() {
    const data = await fetchData('/funnel/applications');
    const qualityData = await fetchData('/applications/quality');
    
    if (!data || !qualityData) return;

    const grid = document.getElementById('kpi-grid');
    
    // Calculate global shortlisting rate
    let totalApps = data.total_applications || 0;
    let shortlisted = data.stages.find(s => s.key === 'candidates_shortlisted')?.count || 0;
    let shortlistRate = totalApps > 0 ? ((shortlisted / totalApps) * 100).toFixed(1) : 0;
    
    // Find below-threshold rejection rate
    let belowRow = qualityData.quality_breakdown.find(r => r.category === 'Below Threshold');
    let rejectionRate = belowRow ? belowRow.rejection_rate : 0;

    grid.innerHTML = `
        <div class="kpi-card">
            <div class="kpi-label">Total Applications</div>
            <div class="kpi-value">${formatNumber(totalApps)}</div>
            <div class="kpi-trend positive"><svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg> Active Pipeline</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Candidates Shortlisted</div>
            <div class="kpi-value">${formatNumber(shortlisted)}</div>
            <div class="kpi-trend positive"><svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path></svg> ${shortlistRate}% Shortlist Rate</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Below Threshold Rejection Rate</div>
            <div class="kpi-value">${rejectionRate}%</div>
            <div class="kpi-trend negative">Filtering functioning</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">Applications Rejected</div>
            <div class="kpi-value">${formatNumber(data.rejected)}</div>
            <div class="kpi-trend negative">Closed Loops</div>
        </div>
    `;
}

async function renderFunnel() {
    const data = await fetchData('/funnel/applications');
    if (!data) return;

    const container = document.getElementById('funnel-container');
    let maxCount = Math.max(...data.stages.map(s => s.count));

    container.innerHTML = data.stages.map((stage, i) => {
        const fillPct = maxCount > 0 ? (stage.count / maxCount) * 100 : 0;
        let convHtml = '';
        if (i > 0) {
            convHtml = `
                <div class="stage-conversion">
                    <div class="conv-label">Conversion</div>
                    <div class="conv-value">${stage.conversion_pct}%</div>
                </div>
            `;
        }
        return `
            <div class="funnel-stage" style="--stage-color: ${stage.color}; --fill-width: ${fillPct}%">
                <div class="stage-info">
                    <div class="stage-name">${stage.stage}</div>
                    <div class="stage-count">${formatNumber(stage.count)}</div>
                </div>
                ${convHtml}
            </div>
        `;
    }).join('');
}

async function renderTrendChart() {
    const data = await fetchData('/trends');
    if (!data) return;

    const ctx = document.getElementById('trendChart').getContext('2d');
    
    const dates = data.trend.map(t => t.event_date.substring(5)); // MM-DD
    const apps = data.trend.map(t => t.applications);
    const shortlists = data.trend.map(t => t.shortlisted);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Applications',
                    data: apps,
                    borderColor: '#96CEB4',
                    backgroundColor: 'rgba(150, 206, 180, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Shortlists',
                    data: shortlists,
                    borderColor: '#00B894',
                    backgroundColor: 'rgba(0, 184, 148, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#94A3B8' } }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94A3B8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94A3B8', maxTicksLimit: 10 }
                }
            }
        }
    });
}

async function renderQualityTable() {
    const data = await fetchData('/applications/quality');
    if (!data) return;

    const tbody = document.getElementById('quality-table-body');
    
    tbody.innerHTML = data.quality_breakdown.map(row => {
        const pillClass = row.category === 'Meets Threshold' ? 'meets' : 'below';
        return `
            <tr>
                <td><span class="category-pill ${pillClass}">${row.category}</span></td>
                <td>${formatNumber(row.total_applications)}</td>
                <td>${formatNumber(row.pending)}</td>
                <td>${formatNumber(row.shortlisted)}</td>
                <td>${formatNumber(row.rejected)}</td>
                <td><strong>${row.shortlist_rate}%</strong></td>
            </tr>
        `;
    }).join('');
}

async function renderQualityStatus() {
    const data = await fetchData('/quality');
    const indicator = document.querySelector('.status-indicator');
    const text = document.getElementById('quality-status');
    
    if (!data) {
        indicator.className = 'status-indicator fail';
        text.textContent = 'API Offline';
        return;
    }

    const failed = data.checks.filter(c => c.status === 'fail');
    const warned = data.checks.filter(c => c.status === 'warn');

    if (failed.length > 0) {
        indicator.className = 'status-indicator fail';
        text.textContent = `${failed.length} Checks Failed`;
    } else if (warned.length > 0) {
        indicator.className = 'status-indicator warn';
        text.textContent = 'Warnings Detected';
    } else {
        indicator.className = 'status-indicator pass';
        text.textContent = 'Data Flowing • All Checks Pass';
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    renderKPIs();
    renderFunnel();
    renderTrendChart();
    renderQualityTable();
    renderQualityStatus();
    
    // Refresh status every 30s
    setInterval(renderQualityStatus, 30000);
});
