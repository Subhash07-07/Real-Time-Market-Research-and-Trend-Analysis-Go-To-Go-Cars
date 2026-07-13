// ==============================
// GO TO GO CARS — MARKET ANALYSIS
// Interactive Dashboard Scripts
// ==============================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initDate();
    initKPIAnimations();
    initScrollAnimations();
    initCharts();
});

// ---------- Navigation ----------
function initNavigation() {
    const navbar = document.getElementById('navbar');
    const links = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section[id]');

    // Scroll effect
    window.addEventListener('scroll', () => {
        navbar.classList.toggle('scrolled', window.scrollY > 50);

        // Active section detection
        let current = '';
        sections.forEach(section => {
            const top = section.offsetTop - 120;
            if (window.scrollY >= top) {
                current = section.getAttribute('id');
            }
        });

        links.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.section === current) {
                link.classList.add('active');
            }
        });
    });

    // Smooth scroll
    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// ---------- Date ----------
function initDate() {
    const dateEl = document.getElementById('currentDate');
    const now = new Date();
    dateEl.textContent = now.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

// ---------- KPI Animations ----------
function initKPIAnimations() {
    const kpiValues = document.querySelectorAll('.kpi-value');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateKPI(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    kpiValues.forEach(kpi => observer.observe(kpi));
}

function animateKPI(el) {
    const target = parseFloat(el.dataset.target);
    const suffix = el.dataset.suffix || '';
    const duration = 1500;
    const start = performance.now();

    function update(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = (target * eased).toFixed(1);
        el.textContent = `$${current}${suffix}`.replace('$$', '$');

        // Fix formatting
        if (suffix === '%') {
            el.textContent = `${(target * eased).toFixed(1)}%`;
        } else if (suffix === 'M') {
            el.textContent = `${Math.round(target * eased)}M`;
        } else if (suffix === 'B') {
            el.textContent = `$${(target * eased).toFixed(1)}B`;
        }

        if (progress < 1) requestAnimationFrame(update);
    }

    requestAnimationFrame(update);
}

// ---------- Scroll Animations ----------
function initScrollAnimations() {
    const animElements = document.querySelectorAll(
        '.kpi-card, .competitor-card, .swot-card, .gap-card, .chart-card, .timeline-phase, .revenue-card'
    );

    animElements.forEach((el, i) => {
        el.classList.add('fade-in');
        el.style.transitionDelay = `${(i % 4) * 0.1}s`;
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    animElements.forEach(el => observer.observe(el));

    // Impact bar animations
    const impactBars = document.querySelectorAll('.impact-fill');
    const barObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.width = entry.target.style.width;
            }
        });
    }, { threshold: 0.5 });
    impactBars.forEach(bar => barObserver.observe(bar));
}

// ---------- Charts ----------
function initCharts() {
    const chartDefaults = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                labels: {
                    color: '#9393a8',
                    font: { family: 'Inter', size: 11, weight: 500 },
                    padding: 16,
                    usePointStyle: true,
                    pointStyleWidth: 8,
                }
            },
            tooltip: {
                backgroundColor: '#1c1c28',
                titleColor: '#f0f0f5',
                bodyColor: '#9393a8',
                borderColor: 'rgba(255,255,255,0.08)',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 12,
                titleFont: { family: 'Inter', weight: 700 },
                bodyFont: { family: 'Inter' },
            }
        }
    };

    Chart.defaults.color = '#9393a8';
    Chart.defaults.font.family = 'Inter';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';

    // 1. Market Growth Chart
    new Chart(document.getElementById('marketGrowthChart'), {
        type: 'line',
        data: {
            labels: ['2022', '2023', '2024', '2025', '2026', '2028', '2030', '2032', '2034'],
            datasets: [{
                label: 'Shared Mobility Market (USD Bn)',
                data: [82, 89, 98, 109.5, 118, 138, 155, 173, 191.2],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.08)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 7,
                pointBackgroundColor: '#6366f1',
                borderWidth: 2.5,
            }, {
                label: 'Ride-Hailing Segment (USD Bn)',
                data: [0.6, 0.72, 0.85, 0.95, 1.15, 1.8, 2.5, 3.1, 3.7],
                borderColor: '#a855f7',
                backgroundColor: 'rgba(168, 85, 247, 0.05)',
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 7,
                pointBackgroundColor: '#a855f7',
                borderWidth: 2.5,
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { color: '#5e5e72', font: { size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#5e5e72', font: { size: 11 } }
                }
            }
        }
    });

    // 2. Radar Chart — Competitor Comparison
    new Chart(document.getElementById('radarChart'), {
        type: 'radar',
        data: {
            labels: ['User Trust', 'Feature Set', 'Market Scale', 'Tech Innovation', 'Revenue Model', 'City Coverage'],
            datasets: [{
                label: 'QuickRide',
                data: [85, 75, 60, 55, 65, 70],
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#22c55e',
            }, {
                label: 'BlaBlaCar',
                data: [75, 55, 95, 60, 80, 85],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#3b82f6',
            }, {
                label: 'sRide',
                data: [90, 85, 45, 80, 40, 55],
                borderColor: '#f97316',
                backgroundColor: 'rgba(249, 115, 22, 0.1)',
                borderWidth: 2,
                pointBackgroundColor: '#f97316',
            }, {
                label: 'Go To Go Cars (Target)',
                data: [92, 95, 30, 90, 75, 60],
                borderColor: '#a855f7',
                backgroundColor: 'rgba(168, 85, 247, 0.08)',
                borderWidth: 2.5,
                borderDash: [5, 5],
                pointBackgroundColor: '#a855f7',
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                r: {
                    angleLines: { color: 'rgba(255,255,255,0.06)' },
                    grid: { color: 'rgba(255,255,255,0.06)' },
                    pointLabels: { color: '#9393a8', font: { size: 11, weight: 500 } },
                    ticks: { display: false },
                    beginAtZero: true,
                    max: 100,
                }
            }
        }
    });

    // 3. BlaBlaCar India Growth
    new Chart(document.getElementById('blablaGrowthChart'), {
        type: 'bar',
        data: {
            labels: ['2020', '2021', '2022', '2023', '2024', '2025', '2026 (Est)'],
            datasets: [{
                label: 'Passengers (Millions)',
                data: [3, 4.5, 7, 9.5, 13.5, 20, 30],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.3)',
                    'rgba(59, 130, 246, 0.35)',
                    'rgba(59, 130, 246, 0.4)',
                    'rgba(59, 130, 246, 0.5)',
                    'rgba(59, 130, 246, 0.6)',
                    'rgba(59, 130, 246, 0.75)',
                    'rgba(59, 130, 246, 0.9)',
                ],
                borderColor: '#3b82f6',
                borderWidth: 1.5,
                borderRadius: 6,
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { color: '#5e5e72', font: { size: 11 } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#5e5e72', font: { size: 11 } }
                }
            }
        }
    });

    // 4. User Demographics
    new Chart(document.getElementById('demographicsChart'), {
        type: 'doughnut',
        data: {
            labels: ['18–24 yrs', '25–34 yrs', '35–44 yrs', '45+ yrs'],
            datasets: [{
                data: [30, 40, 20, 10],
                backgroundColor: ['#6366f1', '#a855f7', '#ec4899', '#f97316'],
                borderColor: '#16161f',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            ...chartDefaults,
            cutout: '65%',
            plugins: {
                ...chartDefaults.plugins,
                legend: {
                    ...chartDefaults.plugins.legend,
                    position: 'bottom',
                }
            }
        }
    });

    // 5. Market Segment Revenue Forecast
    new Chart(document.getElementById('segmentChart'), {
        type: 'bar',
        data: {
            labels: ['Intra-city Carpool', 'Intercity Carpool', 'Ride-Hailing', 'Bike/Scooter Share', 'Corporate Mobility', 'EV Shared Rides'],
            datasets: [{
                label: '2025 (Current)',
                data: [2.8, 4.2, 12, 1.5, 3.5, 0.8],
                backgroundColor: 'rgba(99, 102, 241, 0.6)',
                borderColor: '#6366f1',
                borderWidth: 1,
                borderRadius: 4,
            }, {
                label: '2030 (Projected)',
                data: [6.5, 10.8, 28, 4.2, 9.5, 5.5],
                backgroundColor: 'rgba(168, 85, 247, 0.6)',
                borderColor: '#a855f7',
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.04)' },
                    ticks: { color: '#5e5e72', font: { size: 11 }, callback: v => `$${v}B` }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#5e5e72', font: { size: 11 }, maxRotation: 30 }
                }
            }
        }
    });

    // 6. Market Share — Downloads
    new Chart(document.getElementById('marketShareChart'), {
        type: 'polarArea',
        data: {
            labels: ['BlaBlaCar (100M+)', 'QuickRide (1M+)', 'sRide (1M+)', 'Others'],
            datasets: [{
                data: [100, 5, 3, 15],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.5)',
                    'rgba(34, 197, 94, 0.5)',
                    'rgba(249, 115, 22, 0.5)',
                    'rgba(94, 94, 114, 0.3)',
                ],
                borderColor: '#16161f',
                borderWidth: 2,
            }]
        },
        options: {
            ...chartDefaults,
            scales: {
                r: {
                    grid: { color: 'rgba(255,255,255,0.06)' },
                    ticks: { display: false },
                }
            },
            plugins: {
                ...chartDefaults.plugins,
                legend: {
                    ...chartDefaults.plugins.legend,
                    position: 'bottom',
                }
            }
        }
    });
}
