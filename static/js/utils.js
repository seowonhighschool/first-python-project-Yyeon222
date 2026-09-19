// =========================================
// 카테고리 정의
// =========================================
const CATEGORY_MAP = {
  food:      { label: '식비',    icon: '🍽️', color: '#FF6B6B' },
  cafe:      { label: '카페',    icon: '☕',  color: '#C49A6C' },
  transport: { label: '교통',    icon: '🚌',  color: '#4ECDC4' },
  shopping:  { label: '쇼핑',   icon: '🛍️', color: '#9B59B6' },
  medical:   { label: '의료',    icon: '💊',  color: '#2ECC71' },
  leisure:   { label: '문화/여가', icon: '🎬', color: '#F39C12' },
  etc:       { label: '기타',    icon: '📌',  color: '#95A5A6' },
};

const CATEGORY_COLORS = Object.values(CATEGORY_MAP).map(c => c.color);
const CATEGORY_LABELS = Object.values(CATEGORY_MAP).map(c => `${c.icon} ${c.label}`);

// =========================================
// 포매팅 유틸
// =========================================
function formatCurrency(amount) {
  return `${Number(amount).toLocaleString('ko-KR')}원`;
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  const [year, month, day] = dateStr.split('-');
  return `${year}.${month}.${day}`;
}

function getCategoryLabel(key) {
  const cat = CATEGORY_MAP[key];
  if (!cat) return key;
  return `${cat.icon} ${cat.label}`;
}

function getCurrentMonth() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

// =========================================
// Toast 알림
// =========================================
let toastTimer = null;

function showToast(message, type = 'default') {
  const toast = document.querySelector('#toast');
  const toastMessage = document.querySelector('#toast-message');

  toastMessage.textContent = message;
  toast.className = `toast toast--${type}`;
  toast.hidden = false;

  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.hidden = true;
  }, 2500);
}

// =========================================
// 로딩 오버레이
// =========================================
// 요청 2개가 겹칠 때 먼저 끝난 쪽이 오버레이를 꺼버리지 않도록 호출 수를 센다.
let loadingCount = 0;

function showLoading(visible) {
  loadingCount = visible ? loadingCount + 1 : Math.max(0, loadingCount - 1);
  document.querySelector('#loading-overlay').hidden = loadingCount === 0;
}

// =========================================
// Debounce
// =========================================
// 검색창처럼 입력할 때마다 호출되는 이벤트에 쓴다.
// 없으면 '스타벅스' 입력에 요청이 4번 나가고 오버레이가 4번 깜빡인다.
function debounce(fn, delay = 300) {
  let timer = null;

  return (...args) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// =========================================
// Exports
// =========================================
export {
  CATEGORY_MAP,
  CATEGORY_COLORS,
  CATEGORY_LABELS,
  formatCurrency,
  formatDate,
  getCategoryLabel,
  getCurrentMonth,
  showToast,
  showLoading,
  debounce,
};
