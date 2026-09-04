import {
  showToast,
  showLoading,
  formatCurrency,
  formatDate,
  getCategoryLabel,
  getCurrentMonth,
} from './utils.js';

import {
  parseSMS,
  saveTransaction,
  getTransactions,
  getDashboardStats,
  getAIAnalysis,
} from './api.js';

import {
  renderCategoryChart,
  renderDailyChart,
  renderComparisonChart,
} from './dashboard.js';

// =========================================
// 탭 전환
// =========================================
function initTabs() {
  const tabButtons  = document.querySelectorAll('.tab-nav__item');
  const tabContents = document.querySelectorAll('.tab-content');

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      tabButtons.forEach(b => {
        b.classList.remove('tab-nav__item--active');
        b.setAttribute('aria-selected', 'false');
      });
      tabContents.forEach(c => c.classList.remove('tab-content--active'));

      btn.classList.add('tab-nav__item--active');
      btn.setAttribute('aria-selected', 'true');

      const targetContent = document.querySelector(`[data-tab-content="${target}"]`);
      targetContent.classList.add('tab-content--active');

      if (target === 'dashboard') loadDashboard();
      if (target === 'history')   loadHistory();
      if (target === 'analysis')  loadAnalysis();
    });
  });
}

// =========================================
// Tab 1: 문자 입력
// =========================================
let parsedData = null;

function initInputTab() {
  document.querySelector('#parse-btn').addEventListener('click', handleParse);
  document.querySelector('#reparse-btn').addEventListener('click', resetInput);
  document.querySelector('#save-btn').addEventListener('click', handleSave);
}

async function handleParse() {
  const smsText = document.querySelector('#sms-input').value.trim();

  if (!smsText) {
    showToast('결제 문자를 입력해주세요', 'error');
    return;
  }

  showLoading(true);
  try {
    const res = await parseSMS(smsText);
    if (!res.success) throw new Error(res.error);
    parsedData = res.data;
    renderParseResult(parsedData);
  } catch (err) {
    showToast('분석에 실패했습니다. 다시 시도해주세요', 'error');
    console.error(err);
  } finally {
    showLoading(false);
  }
}

function renderParseResult(data) {
  document.querySelector('#result-store').textContent    = data.store;
  document.querySelector('#result-amount').textContent   = formatCurrency(data.amount);
  document.querySelector('#result-category').textContent = getCategoryLabel(data.category);
  document.querySelector('#result-date').textContent     = `${formatDate(data.date)} ${data.time}`;
  document.querySelector('#result-card').textContent     = data.card || '—';
  document.querySelector('#parse-result').hidden         = false;
}

function resetInput() {
  parsedData = null;
  document.querySelector('#sms-input').value    = '';
  document.querySelector('#parse-result').hidden = true;
}

async function handleSave() {
  if (!parsedData) return;

  showLoading(true);
  try {
    const res = await saveTransaction(parsedData);
    if (!res.success) throw new Error(res.error);
    showToast('저장됐어요! ✅', 'success');
    resetInput();
  } catch (err) {
    showToast('저장에 실패했습니다', 'error');
    console.error(err);
  } finally {
    showLoading(false);
  }
}

// =========================================
// Tab 2: 대시보드
// =========================================
async function loadDashboard() {
  const month = document.querySelector('#dashboard-month').value || getCurrentMonth();

  showLoading(true);
  try {
    const res = await getDashboardStats(month);
    if (!res.success) throw new Error(res.error);

    const { total_amount, by_category, by_date } = res.data;

    document.querySelector('#total-amount').textContent = formatCurrency(total_amount);
    renderCategoryChart(by_category);
    renderDailyChart(by_date);
  } catch (err) {
    showToast('데이터를 불러오지 못했습니다', 'error');
    console.error(err);
  } finally {
    showLoading(false);
  }
}

// =========================================
// Tab 3: 내역 조회
// =========================================
async function loadHistory() {
  const month    = document.querySelector('#history-month').value    || getCurrentMonth();
  const category = document.querySelector('#history-category').value || '';
  const search   = document.querySelector('#history-search').value   || '';

  showLoading(true);
  try {
    const res = await getTransactions({ month, category, search });
    if (!res.success) throw new Error(res.error);
    renderTransactionTable(res.data);
  } catch (err) {
    showToast('내역을 불러오지 못했습니다', 'error');
    console.error(err);
  } finally {
    showLoading(false);
  }
}

function renderTransactionTable(transactions) {
  const tbody = document.querySelector('#transaction-tbody');

  if (!transactions || transactions.length === 0) {
    tbody.innerHTML = `
      <tr class="table__empty-row">
        <td colspan="4">내역이 없습니다</td>
      </tr>`;
    return;
  }

  tbody.innerHTML = transactions.map(t => `
    <tr>
      <td>${formatDate(t.date)}</td>
      <td>${t.store}</td>
      <td>${getCategoryLabel(t.category)}</td>
      <td>${formatCurrency(t.amount)}</td>
    </tr>
  `).join('');
}

// =========================================
// Tab 4: AI 분석
// =========================================
async function loadAnalysis() {
  const ageGroup    = document.querySelector('#analysis-age-group').value;
  const incomeGroup = document.querySelector('#analysis-income-group').value;

  showLoading(true);
  try {
    const res = await getAIAnalysis(ageGroup, incomeGroup);
    if (!res.success) throw new Error(res.error);

    const { user_total, peer_average, by_category, advice } = res.data;

    document.querySelector('#user-total').textContent  = formatCurrency(user_total);
    document.querySelector('#peer-total').textContent  = formatCurrency(peer_average);
    document.querySelector('#advice-text').textContent = advice;

    renderComparisonChart(by_category);
  } catch (err) {
    showToast('분석 데이터를 불러오지 못했습니다', 'error');
    console.error(err);
  } finally {
    showLoading(false);
  }
}

// =========================================
// 초기화
// =========================================
function init() {
  // 탭 전환 초기화
  initTabs();

  // 문자 입력 탭 초기화
  initInputTab();

  // 대시보드 월 선택
  const dashboardMonth = document.querySelector('#dashboard-month');
  dashboardMonth.value = getCurrentMonth();
  dashboardMonth.addEventListener('change', loadDashboard);

  // 내역 조회 필터
  const historyMonth = document.querySelector('#history-month');
  historyMonth.value = getCurrentMonth();

  document.querySelector('#history-month').addEventListener('change', loadHistory);
  document.querySelector('#history-category').addEventListener('change', loadHistory);
  document.querySelector('#history-search').addEventListener('input', loadHistory);

  // AI 분석 새로고침 버튼
  document.querySelector('#refresh-analysis-btn').addEventListener('click', loadAnalysis);
  document.querySelector('#analysis-age-group').addEventListener('change', loadAnalysis);
document.querySelector('#analysis-income-group').addEventListener('change', loadAnalysis);
}

document.addEventListener('DOMContentLoaded', init);
