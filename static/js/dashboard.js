// static/js/dashboard.js
import { CATEGORY_MAP, CATEGORY_COLORS, formatCurrency } from './utils.js';

// Chart 인스턴스 보관 (재렌더링 시 .destroy() 후 재생성)
let categoryChartInstance   = null;
let dailyChartInstance      = null;
let comparisonChartInstance = null;

// =========================================
// 카테고리별 도넛 차트 (대시보드 탭)
// =========================================
function renderCategoryChart(byCategoryData) {
  const ctx = document.querySelector('#category-chart').getContext('2d');

  if (categoryChartInstance) {
    categoryChartInstance.destroy();
    categoryChartInstance = null;
  }

  const keys   = Object.keys(CATEGORY_MAP);
  const labels = keys.map(k => `${CATEGORY_MAP[k].icon} ${CATEGORY_MAP[k].label}`);
  const data   = keys.map(k => byCategoryData[k] || 0);

  categoryChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: CATEGORY_COLORS,
        borderWidth: 2,
        borderColor: '#fff',
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            font: { size: 12 },
            padding: 12,
            usePointStyle: true,
          },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${formatCurrency(ctx.parsed)}`,
          },
        },
      },
    },
  });
}

// =========================================
// 일별 막대 차트 (대시보드 탭)
// =========================================
function renderDailyChart(byDateData) {
  const ctx = document.querySelector('#daily-chart').getContext('2d');

  if (dailyChartInstance) {
    dailyChartInstance.destroy();
    dailyChartInstance = null;
  }

  const labels = byDateData.map(d => d.date.slice(5)); // MM-DD
  const data   = byDateData.map(d => d.amount);

  dailyChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: '지출',
        data,
        backgroundColor: '#4F46E5',
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${formatCurrency(ctx.parsed.y)}`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
        },
        y: {
          grid: { color: '#F3F4F6' },
          ticks: {
            callback: val => `${(val / 10000).toFixed(0)}만`,
          },
        },
      },
    },
  });
}

// =========================================
// 또래 비교 가로 막대 차트 (AI 분석 탭)
// =========================================
function renderComparisonChart(byCategoryData) {
  const ctx = document.querySelector('#comparison-chart').getContext('2d');

  if (comparisonChartInstance) {
    comparisonChartInstance.destroy();
    comparisonChartInstance = null;
  }

  const keys     = Object.keys(CATEGORY_MAP);
  const labels   = keys.map(k => `${CATEGORY_MAP[k].icon} ${CATEGORY_MAP[k].label}`);
  const userData = keys.map(k => byCategoryData[k]?.user     || 0);
  const peerData = keys.map(k => byCategoryData[k]?.peer_avg || 0);

  comparisonChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: '내 지출',
          data: userData,
          backgroundColor: '#4F46E5',
          borderRadius: 4,
        },
        {
          label: '또래 평균',
          data: peerData,
          backgroundColor: '#E5E7EB',
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            font: { size: 12 },
          },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
        },
        y: {
          grid: { color: '#F3F4F6' },
          ticks: {
            callback: val => `${(val / 10000).toFixed(0)}만`,
          },
        },
      },
    },
  });
}

export { renderCategoryChart, renderDailyChart, renderComparisonChart };
