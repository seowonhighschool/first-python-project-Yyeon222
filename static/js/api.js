// static/js/api.js
// Flask 백엔드와의 모든 통신을 이 파일에서 관리한다.

const API_BASE_URL = 'http://localhost:5000/api';

// =========================================
// POST /api/parse — SMS 파싱
// =========================================
async function parseSMS(smsText) {
  try {
    const res = await fetch(`${API_BASE_URL}/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sms: smsText }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('SMS 파싱 실패:', err);
    return { success: false, error: err.message };
  }
}

// =========================================
// POST /api/transactions — 거래 저장
// ⚠️ 이효재와 엔드포인트 추가 협의 필요
// =========================================
async function saveTransaction(data) {
  try {
    const res = await fetch(`${API_BASE_URL}/transactions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('거래 저장 실패:', err);
    return { success: false, error: err.message };
  }
}

// =========================================
// GET /api/transactions — 거래 내역 조회
// =========================================
async function getTransactions({ month, category, search } = {}) {
  try {
    const params = new URLSearchParams();
    if (month)    params.set('month', month);
    if (category) params.set('category', category);
    if (search)   params.set('search', search);

    const res = await fetch(`${API_BASE_URL}/transactions?${params}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('거래 내역 조회 실패:', err);
    return { success: false, error: err.message };
  }
}

// =========================================
// GET /api/stats — 대시보드 통계
// =========================================
async function getDashboardStats(month) {
  try {
    const res = await fetch(`${API_BASE_URL}/stats?month=${month}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('통계 조회 실패:', err);
    return { success: false, error: err.message };
  }
}

// =========================================
// GET /api/analysis — AI 분석 및 또래 비교
// =========================================
async function getAIAnalysis() {
  try {
    const res = await fetch(`${API_BASE_URL}/analysis`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error('AI 분석 조회 실패:', err);
    return { success: false, error: err.message };
  }
}

export {
  parseSMS,
  saveTransaction,
  getTransactions,
  getDashboardStats,
  getAIAnalysis,
};
