
// ========== TABLE FILTER ==========
function filterTable(input, tableId) {
    const filter = input.value.toLowerCase();
    const rows = document.querySelectorAll('#' + tableId + ' tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(filter) ? '' : 'none';
    });
}

// ========== CHART.JS ==========
document.addEventListener('DOMContentLoaded', function() {
    // --- Revenue Chart (Line) ---
    const ctx1 = document.getElementById('revenueChart').getContext('2d');
    new Chart(ctx1, {
        type: 'line',
        data: {
            labels: weekLabels,
            datasets: [{
                label: 'Revenue (₦)',
                data: weekRevenue,
                borderColor: '#F59E0B',
                backgroundColor: 'rgba(245, 158, 11, 0.05)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#F59E0B',
                pointRadius: 4,
                pointHoverRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                y: {
                    ticks: { color: '#8DA68D', font: { size: 10 } },
                    grid: { color: 'rgba(255,255,255,0.04)' },
                },
                x: {
                    ticks: { color: '#8DA68D', font: { size: 10 } },
                    grid: { display: false },
                }
            },
            interaction: {
                intersect: false,
                mode: 'index',
            },
        }
    });

    // --- Order Status Chart (Doughnut) ---
    const ctx2 = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: statusLabels,
            datasets: [{
                data: statusData,
                backgroundColor: ['#34D399', '#F59E0B', '#3B82F6', '#EF4444'],
                borderColor: '#0B170B',
                borderWidth: 3,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#8DA68D',
                        font: { size: 10 },
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle',
                    }
                }
            },
            cutout: '65%',
        }
    });
});



// ========== ADD BUTTONS ==========
document.querySelectorAll('.table-actions .btn-sm').forEach(btn => {
    btn.addEventListener('click', function() {
        alert('➕ Add new item form would open here.');
    });
});

// ========== NOTIFICATION CLICK ==========
document.querySelector('.notification')?.addEventListener('click', function() {
    alert('🔔 You have 3 unread notifications.');
});

// ========== ADMIN PROFILE CLICK ==========
document.querySelector('.admin-profile')?.addEventListener('click', function() {
    alert('👤 Admin profile settings would open here.');
});



