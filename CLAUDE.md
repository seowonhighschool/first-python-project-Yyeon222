# CLAUDE.md — SMS Budget Tracker (문자 기반 자동 가계부)

> 이 파일은 Claude가 프로젝트 맥락을 바로 이해하도록 만든 지침서다.
> **실제 코드가 이 문서와 다르면 코드를 먼저 확인하고**, 불일치는 사용자에게 알린 뒤 진행한다.

---

## 1. 프로젝트 개요

카드 결제 문자(SMS)를 텍스트로 입력하면 **Gemini API**가 금액·상점명·일시·카드사를 추출하고 카테고리로 분류해 DB에 저장한다. 이후 나이대·소득 수준이 비슷한 또래 그룹의 평균 소비와 비교하고, 맞춤형 소비 개선 조언을 제공한다.

- 참고 서비스: 토스 (카드 연동 기반 소비 분류)
- 기대효과: 가계부 작성 시간 90% 이상 단축 / Chart.js 소비 패턴 시각화 / 또래 비교를 통한 소비 억제
- 개발 일정(5일): 환경 구축 → SMS 파싱 → 통계·또래 비교 API → 4탭 프론트 → 통합 테스트·완성도 향상

## 2. 팀 · 협업 방식

- **박도연**, **이효재** 2인 팀. 계획서상 역할은 나뉘어 있으나 **실제로는 프론트·백엔드 구분 없이 전체 코드를 함께 작성**한다.
- Claude는 요청에 따라 **프론트엔드(HTML/CSS/JS)와 백엔드(Python/Flask/SQLite) 모두** 도와준다.
- 구조·설계 논의, 코드 충돌, 프론트-백엔드 인터페이스 불일치가 생기면 해결 방향을 함께 제시한다.
- 사용자(박도연)는 **한국어로 편하게** 소통하고, 에러는 **스크린샷**으로 공유하는 경우가 많다. 스크린샷이 오면 내용을 읽고 원인 분석 → 수정 코드 순서로 답한다.

## 3. 현재 진행 상황 (2026-09-19 기준)

### 완료
- Flask + SQLite + Vanilla JS 웹앱 골격, GitHub 저장소 연동 (`seowonhighschool` org, `first-python-project-Yyeon222`, **`dev` 브랜치**), 이효재 collaborator 추가
- 영문 README 작성 (shields.io 배지 포함, 프로젝트가 인상적으로 보이는 것을 중시)
- `peer_averages` 테이블 확장: **연령대 × 소득 구간 × 카테고리** 구조, KOSIS 가계 지출 데이터 기반 **224행** 시드
- `/api/analysis` 엔드포인트 및 프론트 드롭다운(연령대·소득 구간) 필터링 — **end-to-end 동작 확인 완료**
- 중첩 `.git` 폴더 문제 → **GitHub에서 깨끗하게 re-clone**하여 해결
- **`POST /api/parse` 500 해결** (원인: Gemini 모델명 은퇴. 아래 19절 참조)
- 내역 조회의 카테고리 필터·상점명 검색 백엔드 구현 (기존엔 프론트만 파라미터를 보내고 백엔드가 무시)
- 거래 중복 저장 버그 수정 (`/api/parse`가 저장까지 하고 있었음)
- `requirements.txt` UTF-16 → UTF-8 재작성 (UTF-16이면 `pip install -r`이 실패)

### 다음 할 일
- 로딩 스피너 중첩 가드, 검색 입력 debounce
- `renderTransactionTable`의 `innerHTML` 이스케이프 처리
- `style.css`의 `[hidden]` 규칙이 `:root` 안에 중첩된 구조 정리
- Chart.js CDN 버전 고정
- 제출 전 `app.run(debug=True)` 및 `str(e)` 노출 점검
- 마무리 단계에서 **GitHub Actions로 Pylint** 추가 검토

### 알려진 제약
- Gemini가 간헐적으로 **503 UNAVAILABLE**(과부하)을 반환한다. 재시도하면 성공한다. 시연 전 재시도 로직 도입을 검토할 것.

## 4. 기술 스택 · 개발 환경

| 영역 | 기술 |
|---|---|
| 백엔드 | Python 3, Flask |
| DB | SQLite |
| 프론트엔드 | Vanilla JS (ES6+), HTML5, CSS3 |
| 시각화 | Chart.js |
| AI | Google Gemini API — SDK `google-genai`, 모델 **`gemini-3.8-flash`** |
| 환경변수 | python-dotenv (`.env`) |
| 협업 | GitHub (GitHub Classroom), VS Code |

- 환경: **Windows + PowerShell + Python venv**
- **모델명은 `gemini_parser.MODEL_NAME` 한 곳에서만 관리한다.** 다른 파일에 모델명을 하드코딩하지 않는다.
  - `gemini-2.5-flash`는 **신규 사용자에게 404로 차단**되어 더 이상 쓸 수 없다.
  - 모델이 또 은퇴하면 `client.models.list()`로 사용 가능한 목록을 먼저 확인한다.
- `requirements.txt`는 **UTF-8로 저장**한다. PowerShell에서 `pip freeze > requirements.txt`를 하면 UTF-16으로 저장되어 설치가 깨진다.
- 서버 실행: `python app.py` → `http://localhost:5000`

## 5. 파일 구조

```
project-root/
├── app.py                  # Flask 엔트리포인트
├── database.py             # DB 처리 로직
├── gemini_parser.py        # Gemini API 파싱 모듈 (모델명·클라이언트 단일 관리)
├── seed.py                 # 또래 비교 데이터 초기 삽입
├── requirements.txt        # UTF-8, 직접 의존성만
├── .env                    # API 키 (커밋 금지, 로컬 전용)
├── .env.example            # 키 형식 템플릿 (커밋 대상)
├── .gitignore
├── static/
│   ├── css/style.css
│   └── js/
│       ├── main.js         # 탭 전환 및 앱 초기화
│       ├── api.js          # Flask API 호출 모듈 (공통 request 헬퍼)
│       ├── dashboard.js    # Chart.js 시각화
│       └── utils.js        # 공통 유틸
└── templates/
    └── index.html          # 단일 페이지
```

- `api.js`가 `export`를 사용하므로 `index.html`에서 `<script type="module">`로 로드한다.
- **VS Code는 프로젝트 루트 폴더 하나만** 연다 (중첩 `.git` 재발 방지).

## 6. 화면 구성 (4탭)

| 탭 | 이름 | 주요 기능 |
|---|---|---|
| 1 | 문자 입력 | SMS 입력 → Gemini 파싱 요청 → 결과 미리보기 → 저장하기 |
| 2 | 대시보드 | 월별/카테고리별 소비 Chart.js 시각화 |
| 3 | 내역 조회 | 전체 거래 테이블 (월·카테고리 필터, 상점명 검색) |
| 4 | AI 분석 | 또래 그룹 비교(연령대·소득 드롭다운) + Gemini 맞춤 조언 |

> 탭1에서 **"분석하기"는 저장하지 않는다.** 미리보기를 확인한 뒤 "저장하기"를 눌러야 DB에 들어간다.

## 7. 코딩 컨벤션

### JavaScript
- 변수/함수 `camelCase`, 상수 `UPPER_SNAKE_CASE`
- `async/await` 사용, `.then()` 체이닝 지양
- **모든 `fetch`는 `try/catch` 필수** — `api.js`의 공통 `request()` 헬퍼가 담당한다
- 실패 시 **응답 본문의 `error` 메시지를 살린다.** `HTTP ${status}`만 던지면 백엔드가 보낸 원인이 사라진다
- DOM 선택은 `querySelector` / `querySelectorAll` (`getElementById` 지양)
- 이벤트는 `addEventListener` (인라인 `onclick` 지양)
- 기능별 파일 분리, 전역 오염 최소화

```js
// 올바른 예시 — api.js의 공통 헬퍼를 통해 호출한다
export async function getTransactions({ month, category, search } = {}) {
  const params = new URLSearchParams();
  if (month)    params.set('month', month);
  if (category) params.set('category', category);
  if (search)   params.set('search', search);

  return request(`/transactions?${params}`, {}, '거래 내역 조회');
}
```

### CSS
- BEM 느슨하게 (`블록__요소--수정자`)
- 레이아웃 단위 `rem` / `%` / `fr`, 보더·그림자는 `px`
- 색상은 CSS 변수로 최상단에 정의
- 모바일 퍼스트, 브레이크포인트 `max-width: 768px`

```css
:root {
  --color-primary: #4F46E5;
  --color-accent: #10B981;
  --color-bg: #F9FAFB;
  --color-text: #111827;
  --radius-md: 8px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
}
```

### HTML
- 시맨틱 태그 (`<main>`, `<section>`, `<header>`, `<nav>`)
- JS 연결은 `data-*` 속성 (예: `data-tab="dashboard"`)
- 필요한 곳에 `aria-label`, `role` 추가

### Python (Flask)
- 함수/변수 `snake_case`, 상수 `UPPER_SNAKE_CASE`
- **에러 응답은 항상** `{"success": false, "error": "메시지"}` 형태로 통일
- **상태코드를 구분한다**: 클라이언트 입력 문제는 `400`, 서버/DB 문제는 `500`, Gemini 등 외부 API 실패는 `502`
- 환경변수는 하드코딩 금지, `os.getenv()`로만 읽기
- Gemini 호출은 **`gemini_parser` 모듈을 통해서만** 한다 (모델명이 갈라지지 않게)

```python
@app.route('/api/parse', methods=['POST'])
def parse_sms():
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('sms'):
            return jsonify({"success": False, "error": "sms 필드가 없습니다"}), 400

        result = gemini_parser.parse_sms(data['sms'])
        if not result['success']:
            status = result.pop('status', 500)
            return jsonify({"success": False, "error": result['error']}), status

        return jsonify({"success": True, "data": result['data']})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

## 8. API 규칙 · 스키마

프론트의 Flask 통신은 **`static/js/api.js`에 집중**한다.

```js
const API_BASE_URL = 'http://localhost:5000/api';

export async function parseSMS(smsText) { ... }
export async function saveTransaction(data) { ... }
export async function getTransactions(params) { ... }
export async function getDashboardStats(month) { ... }
export async function getAIAnalysis(ageGroup, incomeGroup, month) { ... }
```

> ⚠️ 아래는 팀이 합의한 스키마다. **임의 변경 금지.** 변경이 필요하면 먼저 제안하고 확인을 받은 뒤 이 문서를 갱신한다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/api/parse` | SMS 파싱 **(미리보기 전용, 저장하지 않음)** |
| POST | `/api/transactions` | 거래 저장 |
| GET | `/api/transactions?month=&category=&search=` | 거래 내역 (월·카테고리·상점명 검색) |
| GET | `/api/stats?month=YYYY-MM` | 대시보드 통계 |
| GET | `/api/analysis?month=&age_group=&income_group=` | AI 분석 + 또래 비교 |

**`POST /api/parse`** — 파싱만 하고 저장하지 않는다. 응답에 `id`가 없다.
```json
// Request
{ "sms": "[신한카드] 승인 12,000원 스타벅스 07/14 14:32 잔여한도 2,450,000원" }

// Response
{
  "success": true,
  "data": {
    "amount": 12000, "store": "스타벅스", "category": "cafe",
    "date": "2026-07-14", "time": "14:32", "card": "신한카드"
  }
}
```

**`POST /api/transactions`** — `/api/parse` 응답의 `data`를 그대로 보내면 된다.
`amount / store / category / date / time`은 필수, `card`는 선택. 누락 시 `400`.
```json
{ "success": true, "data": { "id": 12 } }
```

**`GET /api/transactions`**
쿼리 파라미터: `month`(`YYYY-MM`), `category`(7개 key 중 하나), `search`(상점명 부분 일치). 전부 선택.
```json
{
  "success": true,
  "data": [
    { "id": 1, "amount": 12000, "store": "스타벅스", "category": "cafe",
      "date": "2026-07-14", "time": "14:32", "card": "신한카드" }
  ],
  "total": 1
}
```

**`GET /api/stats`**
```json
{
  "success": true,
  "data": {
    "total_amount": 352000,
    "by_category": { "food": 120000, "cafe": 45000, "transport": 38000,
                     "shopping": 89000, "medical": 0, "leisure": 60000, "etc": 0 },
    "by_date": [ { "date": "2026-07-01", "amount": 15000 } ]
  }
}
```
`by_category`는 항상 7개 key가 모두 들어있다 (없으면 0).

**`GET /api/analysis`**
쿼리 파라미터: `month`(기본값 이번 달), `age_group`(기본값 `20대초반`), `income_group`(기본값 `mid-low`).
**연령대 값은 한글이므로 프론트에서 `URLSearchParams`로 인코딩해 보낸다.**
```json
{
  "success": true,
  "data": {
    "user_total": 352000,
    "peer_average": 298000,
    "peer_group": "20대초반 / mid-low",
    "has_peer_data": true,
    "by_category": {
      "food": { "user": 120000, "peer_avg": 95000 },
      "cafe": { "user": 45000, "peer_avg": 32000 }
    },
    "advice": "이번 달 카페 지출이 또래 평균보다 40% 높습니다. ..."
  }
}
```
- `peer_average`는 해당 그룹의 **전 카테고리 합계**다.
- `has_peer_data`가 `false`면 그 그룹의 시드 데이터가 없다는 뜻이다. 프론트는 `0원` 대신 **"데이터 없음"** 으로 표시한다.
- `peer_group`은 반드시 화면에 표시한다. 표시하지 않으면 드롭다운이 실제로 반영되는지 눈으로 확인할 수 없다.

**`installment`(할부)는 스키마에서 제외한다.** DB 컬럼도 파싱 대상도 아니다.

## 9. DB 스키마

**컬럼명 규칙:** API 응답 JSON의 key와 DB 컬럼명을 **1:1로 일치**시킨다. 임의 변경 금지.

```sql
-- transactions
CREATE TABLE transactions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  amount     INTEGER NOT NULL,
  store      TEXT    NOT NULL,
  category   TEXT    NOT NULL,
  date       TEXT    NOT NULL,
  time       TEXT    NOT NULL,
  card       TEXT,
  created_at TEXT    DEFAULT (datetime('now', 'localtime'))
);

-- peer_averages (연령대 × 소득 구간 × 카테고리)
CREATE TABLE peer_averages (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  age_group    TEXT    NOT NULL,
  income_group TEXT    NOT NULL,
  category     TEXT    NOT NULL,
  avg_amount   INTEGER NOT NULL,
  UNIQUE(age_group, income_group, category)
);
```

시드 규모: **224행 = 8 연령대 × 4 소득 구간 × 7 카테고리**

| 구분 | 값 |
|---|---|
| `age_group` | `10대` `20대초반` `20대후반` `30대초반` `30대후반` `40대` `50대` `60대이상` |
| `income_group` | `low` `mid-low` `mid-high` `high` |
| `category` | 아래 10절의 7개 key |

- 시드 데이터는 `seed.py`를 실행해 삽입한다 (하드코딩·외부 API 사용 금지). 값 수정은 코드 로직이 아닌 시드 데이터만 바꾸고 재실행한다.
- `*.db`는 `.gitignore` 대상이므로 **클론 후 DB 재생성이 필요**하다: `python app.py`로 한 번 띄워 테이블을 만든 뒤(`init_db()`가 import 시 실행됨) `python seed.py`.
- `database.py`의 `_migrate_peer_averages`는 **구스키마를 만나면 테이블을 DROP한다.** 마이그레이션 후에는 `seed.py`를 반드시 다시 실행해야 한다. 안 하면 또래 비교가 조용히 전부 0이 된다.

## 10. 소비 카테고리 (7개 고정)

| 카테고리 | key | 아이콘 | 색상 |
|---|---|---|---|
| 식비 | `food` | 🍽️ | `#FF6B6B` |
| 카페 | `cafe` | ☕ | `#C49A6C` |
| 교통 | `transport` | 🚌 | `#4ECDC4` |
| 쇼핑 | `shopping` | 🛍️ | `#9B59B6` |
| 의료 | `medical` | 💊 | `#2ECC71` |
| 문화/여가 | `leisure` | 🎬 | `#F39C12` |
| 기타 | `etc` | 📌 | `#95A5A6` |

- Chart.js 색상 배열도 **위 순서 그대로** 유지한다 (`utils.js`의 `CATEGORY_MAP`에서 파생된다).
- **7개 외의 값이 저장되면 통계에서 조용히 누락된다.** `gemini_parser`가 화이트리스트로 검증해 `etc`로 보정한다.

## 11. Gemini 연동

- Gemini 호출은 **백엔드(Flask)에서만**, 그중에서도 **`gemini_parser` 모듈을 통해서만** 수행한다.
- SDK: `google-genai`, 모델: **`gemini_parser.MODEL_NAME`** (현재 `gemini-3.8-flash`). 키는 `os.getenv("GEMINI_API_KEY")`.
- 클라이언트는 **지연 생성**한다. 모듈 최상단에서 만들면 키가 없을 때 `import` 단계에서 서버가 아예 뜨지 않는다.
- SMS → JSON 변환은 아래 프롬프트를 **고정**으로 사용한다.

```
다음 카드 결제 문자에서 정보를 추출해줘.
반드시 아래 JSON 형식으로만 응답해. 다른 말은 절대 하지 마.

{
  "amount": 숫자 (원 단위 정수, 쉼표 없이),
  "store": "상점명",
  "category": "food|cafe|transport|shopping|medical|leisure|etc 중 하나",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "card": "카드사명"
}

오늘은 {today}이다. 문자에 연도가 없으면 {current_year}년으로 간주해라.

SMS: {sms_text}
```

**파싱 규칙**
- 프롬프트에 JSON 중괄호가 있으므로 `str.format()`은 `KeyError`를 낸다 → `.replace("{sms_text}", sms)` 사용
- **기준 연도를 반드시 넣는다.** 없으면 `07/14` 같은 문자를 과거 연도로 추론해 월별 통계에서 누락된다
- 응답은 `json.loads()`로 파싱 (코드펜스 ```` ```json ```` 가 섞이면 제거 후 파싱)
- `amount`는 `'12,000'`/`'12000원'` 형태로 올 수 있으므로 숫자만 추출해 `int` 변환
- `category`가 7개 고정값이 아니면 `"etc"`로 보정
- 필수 필드(`amount` `store` `category` `date` `time`)가 없으면 400으로 응답

## 12. 보안 · `.env`

**핵심 원칙**
- `.env`는 **절대 커밋하지 않는다.** API 키를 JS 코드에 하드코딩하지 않는다.
- 흐름: `[JS fetch()] → /api/parse (Flask) → Gemini API` (`GEMINI_API_KEY`는 Flask에서만 사용)
- **Claude는 코드 작성 시 API 키가 JS 파일이나 커밋 대상 파일에 들어가지 않도록 능동적으로 경고한다.** 사용자에게 실제 키 값을 채팅에 붙여넣으라고 요청하지 않으며, `.env` 파일은 사용자가 직접 만든다.

| 파일 | GitHub | 용도 |
|---|---|---|
| `.env` | ❌ 금지 | 실제 API 키 |
| `.env.example` | ✅ | 키 형식 템플릿 |
| `.gitignore` | ✅ | `.env` 커밋 차단 |

```
# .gitignore 필수 내용
.env
__pycache__/
*.pyc
*.db
venv/
.DS_Store
```

**환경변수**

| 이름 | 필수 | 설명 |
|---|---|---|
| `GEMINI_API_KEY` | ✅ | Google AI Studio 발급 키 |
| `DB_PATH` | ❌ | SQLite 경로 (기본값 `database.db`) |

**주의**
- `.gitignore`는 첫 커밋 **이전에** 생성한다. 커밋 전 `git status`로 `.env`가 목록에 없는지 확인한다.
- 이미 `.env`를 커밋했다면 **API 키를 즉시 재발급**한다.
- `.env`는 git이 추적하지 않으므로 **re-clone 시 수동으로 백업·재생성**해야 한다.

## 13. Chart.js 지침

- Chart 인스턴스는 재렌더링 시 **반드시 `.destroy()` 후 재생성**
- 색상 팔레트는 CSS 변수·카테고리 색상과 일관되게
- 옵션: `responsive: true, maintainAspectRatio: false`
- 도넛/파이: 카테고리별 비율 / 막대: 월별 추이 / 라인: 일별 누적

## 14. GitHub 협업 규칙

- 브랜치: `main`(배포), `dev`(개발), `feat/기능명`(기능 개발). 현재 작업은 `dev`
- **`dev`가 `main`보다 뒤처지지 않게 관리한다.** 2026-09-19에 두 브랜치가 갈라져 `main`에만 기능 작업이 쌓여 있었고, `main`을 `dev`로 머지해 정리했다.
- 커밋 메시지: `[feat] SMS 입력 UI 구현` / `[fix] 차트 리렌더링 오류 수정` / `[style] 대시보드 레이아웃 조정`
- PR 전 `dev`에서 충돌 해결 후 머지

## 15. 디자인 방향

- 깔끔하고 신뢰감 있는 **핀테크 스타일 (토스 참고)**
- 주색 인디고 `#4F46E5` + 포인트 에메랄드 `#10B981`
- 폰트: `-apple-system, BlinkMacSystemFont, 'Pretendard'` (시스템 폰트 기본)
- 카드 UI: `border-radius: 12px`, `box-shadow: 0 2px 8px rgba(0,0,0,0.08)`
- **로딩 스피너 · 성공 토스트 · 에러 메시지는 항상 구현**
- 에러 토스트에는 **백엔드가 보낸 실제 원인 메시지**를 띄운다

## 16. 파싱 대상 SMS 예시 (UI 안내문구·플레이스홀더 참고)

```
[신한카드] 승인 12,000원 스타벅스 07/14 14:32 잔여한도 2,450,000원
[KB국민카드] 홍길동님 12,000원(일시불) 07/14 14:32 스타벅스 승인완료
삼성카드(1234) 12,000원 스타벅스 승인완료 07/14 14:32
[현대카드] 07/14 14:32 스타벅스 12,000원 승인 (일시불)
```

입력창 플레이스홀더: `[신한카드] 승인 12,000원 스타벅스 07/14 14:32 잔여한도 2,450,000원`

## 17. Claude 응답 방식

**코드 요청 시**
1. 변경/추가할 **파일명을 먼저** 명시하고, 코드 블록 상단에 경로 주석 표기 (`// static/js/api.js`)
2. 사용자는 **바로 복붙해서 쓸 수 있는 완성된 코드**를 선호한다 → 함수·블록 단위로 **완결된 코드**를 주고, "어디에 넣는지"는 한 줄로 명확히 알려준다. 스니펫 조각만 던져놓고 사용자가 끼워 맞추게 하지 않는다.
3. 파일 전체 재작성은 구조적으로 필요할 때만 하고, 그 경우 **이유를 먼저 설명**한다 (설명 없이 통째로 갈아엎지 않는다).
4. 변경 이유는 1~2줄로 간략히.

**설명 요청 시:** 결론 먼저, 이유는 간략하게, 불필요한 배경 생략. **한국어로 응답**(기술 용어·변수명은 영어 유지).

**여러 방법이 있을 때:** 권장안 1개를 먼저 제시하고 대안은 "다른 방법:"으로 구분.

**디버깅 시:** 에러 메시지/스크린샷/상황 설명 → 원인 분석 → 수정 코드 순서. 사용자는 구조가 꼬이면 **처음부터 깔끔하게 다시 하는 방식**(예: re-clone)을 선호한다.

## 18. Claude가 하지 말아야 할 것

- 요청하지 않은 기능을 임의로 추가하지 않는다
- 설명 없이 전체 파일을 새로 작성하지 않는다
- `.env`나 API 키 관련 코드를 프론트엔드 JS에 포함시키지 않는다
- 프론트-백엔드 **API 스키마를 임의로 변경하지 않는다** — 필요하면 먼저 제안하고 확인받는다
- DB 컬럼명과 API JSON key를 서로 다르게 만들지 않는다
- 모델명을 `gemini_parser.MODEL_NAME` 밖에 하드코딩하지 않는다

## 19. 트러블슈팅 메모 (겪었던 문제)

| 문제 | 해결 |
|---|---|
| `POST /api/parse` 500 | **모델 `gemini-2.5-flash`가 신규 사용자에게 404로 차단됨.** `gemini-3.8-flash`로 교체. 서버 터미널 traceback을 먼저 볼 것 |
| `pip install -r requirements.txt` 실패 | PowerShell `pip freeze >`가 **UTF-16**으로 저장. UTF-8로 재작성 |
| 키가 없으면 서버가 아예 안 뜸 | `genai.Client()`를 모듈 최상단에서 생성하면 import가 터진다 → **지연 생성**으로 변경 |
| 거래가 두 번 저장됨 | `/api/parse`와 `/api/transactions` 양쪽에서 insert하고 있었음 → 저장은 후자 하나로 |
| 필터·검색이 동작 안 함 | 프론트는 파라미터를 보내는데 백엔드가 안 읽고 있었음 |
| 드롭다운이 반영 안 됨 | `api.js`가 파라미터를 쿼리스트링에 안 붙이고 있었음. `peer_group`을 화면에 표시해 재발 방지 |
| 연도 없는 문자가 과거 연도로 저장 | 프롬프트에 **기준 연도** 추가 |
| 토스트에 `HTTP 500`만 표시 | `api.js`가 응답 본문을 안 읽고 throw → 공통 `request()`에서 `error` 메시지 사용 |
| 중첩 `.git` 폴더로 git이 전체 파일을 삭제된 것으로 표시 | 깨끗하게 re-clone, 이후 루트 폴더 하나만 VS Code로 열기 |
| re-clone 후 Gemini 호출 실패 | `.env`는 git 미추적 → 수동 재생성 (키 재입력) |
| PowerShell에서 venv 활성화 차단 | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Gemini 503 UNAVAILABLE | 일시적 과부하. 재시도하면 성공 |
