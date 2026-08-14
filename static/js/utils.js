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
function showLoading(visible) {
  document.querySelector('#loading-overlay').hidden = !visible;
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
};
