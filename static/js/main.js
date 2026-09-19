import {
  showToast,
  showLoading,
  formatCurrency,
  formatDate,
  getCategoryLabel,
  getCurrentMonth,
  debounce,
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
    showToast(err.message || '분석에 실패했습니다. 다시 시도해주세요', 'error');
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
    showToast(err.message || '저장에 실패했습니다', 'error');
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
    showToast(err.message || '데이터를 불러오지 못했습니다', 'error');
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
    showToast(err.message || '내역을 불러오지 못했습니다', 'error');
    console.error(err);
  } finally {
    showLoading(false);
  }
}

function renderTransactionTable(transactions) {
  const tbody = document.querySelector('#transaction-tbody');
  tbody.textContent = '';

  if (!transactions || transactions.length === 0) {
    const row  = document.createElement('tr');
    const cell = document.createElement('td');
    row.className = 'table__empty-row';
    cell.colSpan = 4;
    cell.textContent = '내역이 없습니다';
    row.append(cell);
    tbody.append(row);
    return;
  }

  // 상점명은 사용자가 붙여넣은 문자에서 나온 값이라 innerHTML로 넣으면 안 된다.
  // textContent로 채우면 어떤 문자열이 와도 스크립트로 실행되지 않는다.
  const fragment = document.createDocumentFragment();

  transactions.forEach(t => {
    const row = document.createElement('tr');

    [
      formatDate(t.date),
      t.store,
      getCategoryLabel(t.category),
      formatCurrency(t.amount),
    ].forEach(value => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.append(cell);
    });

    fragment.append(row);
  });

  tbody.append(fragment);
}

// =========================================
// Tab 4: AI 분석
// =========================================
async function loadAnalysis() {
  const ageGroup    = document.querySelector('#analysis-age-group').value;
  const incomeGroup = document.querySelector('#analysis-income-group').value;
  const month       = document.querySelector('#dashboard-month').value || getCurrentMonth();

  showLoading(true);
  try {
    const res = await getAIAnalysis(ageGroup, incomeGroup, month);
    if (!res.success) throw new Error(res.error);

    const { user_total, peer_average, peer_group, has_peer_data, by_category, advice } = res.data;

    document.querySelector('#user-total').textContent  = formatCurrency(user_total);
    document.querySelector('#advice-text').textContent = advice;

    // 어느 그룹과 비교했는지 화면에 표시한다 (드롭다운이 실제로 반영되는지 눈으로 확인 가능)
    document.querySelector('#peer-label').textContent = `또래 평균 (${peer_group})`;

    // 또래 데이터가 없으면 0원 대신 '데이터 없음'으로 구분해서 보여준다
    document.querySelector('#peer-total').textContent =
      has_peer_data ? formatCurrency(peer_average) : '데이터 없음';

    renderComparisonChart(by_category);
  } catch (err) {
    showToast(err.message || '분석 데이터를 불러오지 못했습니다', 'error');
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
  // 타이핑 중에는 마지막 입력 후 300ms 뒤에 한 번만 요청한다
  document.querySelector('#history-search').addEventListener('input', debounce(loadHistory, 300));

  // AI 분석 새로고침 버튼
  document.querySelector('#refresh-analysis-btn').addEventListener('click', loadAnalysis);
  document.querySelector('#analysis-age-group').addEventListener('change', loadAnalysis);
  document.querySelector('#analysis-income-group').addEventListener('change', loadAnalysis);
}

document.addEventListener('DOMContentLoaded', init);
