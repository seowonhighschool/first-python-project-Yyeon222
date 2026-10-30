<div align="center">
  <h1>💳 SMS Budget Tracker</h1>
  <p><strong>Paste a payment text. AI does the rest.</strong></p>
  <p>An intelligent expense manager that parses Korean card SMS messages using Google Gemini, categorizes your spending, and benchmarks it against peers.</p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white" />
    <img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" />
    <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" />
  </p>
  <p>
    <img src="https://img.shields.io/badge/Google_Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" />
    <img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white" />
    <img src="https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge" />
  </p>
  <p>
    <a href="https://github.com/seowonhighschool/first-python-project-Yyeon222/actions/workflows/pylint.yml"><img src="https://github.com/seowonhighschool/first-python-project-Yyeon222/actions/workflows/pylint.yml/badge.svg" alt="CI" /></a>
    <img src="https://img.shields.io/badge/tests-129_passing-10B981?style=flat-square&logo=pytest&logoColor=white" />  </p>
</div>

---

##  Features

-  **Zero-effort logging** — paste any Korean card SMS and Gemini extracts amount, merchant, date, and time automatically
-  **Bulk paste** — paste a whole month of messages at once; one Gemini call extracts every payment and skips ads and cancellations
-  **Smart categorization** — spending is sorted into 7 categories, and you can fix the category before saving
-  **Visual dashboard** — category donut, cumulative daily line, and a 6-month trend chart powered by Chart.js
-  **Monthly budget** — set a budget and see how much is left, with a warning at 80% and when you go over
-  **Month-over-month** — "▲ ₩15,000 more than last month" at a glance
-  **Peer benchmarking** — compare your spending against your age and income group (224 KOSIS-based data points)
-  **Personalized advice** — Gemini analyzes your habits and suggests actionable improvements (cached to save API quota)
-  **Transaction history** — filter, search, edit, and delete
-  **Accounts** — sign up and log in; every user sees only their own data
-  **Resilient AI calls** — 15-second timeout and automatic fallback across three Gemini models
-  **Dark premium UI** — mobile-first, Pretendard font, works on any phone on the same Wi-Fi

---

##  Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python, Flask |
| Database | SQLite |
| Frontend | Vanilla JS (ES6+), HTML5, CSS3 |
| Visualization | Chart.js |
| AI | Google Gemini API (`google-genai`) |
| Auth | Flask session cookies + Werkzeug password hashing |
| Config | python-dotenv |
| Testing & CI | pytest, Pylint, GitHub Actions |

---

##  Project Structure

```
sms-budget-tracker/
├── app.py                  # Flask entry point & routing
├── database.py             # DB init and CRUD
├── gemini_parser.py        # Gemini API integration
├── seed.py                 # Seed peer comparison data (runs automatically on first start)
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
├── .github/workflows/
│   └── pylint.yml          # Pylint + pytest on every push / PR
├── tests/                  # 129 tests — Gemini is faked, no API key needed
├── static/
│   ├── css/style.css
│   └── js/
│       ├── main.js         # Tab switching & app init
│       ├── auth.js         # Login / sign-up screen
│       ├── api.js          # Backend API calls
│       ├── dashboard.js    # Chart.js visualizations
│       └── utils.js        # Shared utilities
└── templates/
    └── index.html          # Single-page layout
```

---

##  Getting Started

### Prerequisites

- Python 3.10+
- A [Google Gemini API key](https://aistudio.google.com/)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/seowonhighschool/first-python-project-Yyeon222.git
cd first-python-project-Yyeon222

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
copy .env.example .env
# Open .env and fill in GEMINI_API_KEY and SECRET_KEY

# 5. Run the server (creates the database and seeds peer data on first start)
python app.py
```

Open `http://localhost:5000` in your browser and sign up.
The first account to sign up takes over any transactions saved before accounts existed.

### Running the tests

```bash
pip install pytest
python -m pytest -q
```

Gemini is replaced with a fake and each test uses a temporary database, so no API key or network is needed.

### Access from other devices on the same Wi-Fi

The server binds to `0.0.0.0` by default, so phones and laptops on the same network can reach it.
On startup the terminal prints the LAN address:

```
이 컴퓨터    : http://localhost:5000
같은 와이파이: http://192.168.0.12:5000
```

On Windows you need to allow the port once, from an **administrator** PowerShell:

```powershell
New-NetFirewallRule -DisplayName "SMS Budget Tracker (5000)" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow -Profile Private
```

> **Note** This opens the app to everyone on your network. Keep `FLASK_DEBUG` off (the default) —
> the Werkzeug debugger allows arbitrary code execution if exposed.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | O | — | Google AI Studio API key |
| `SECRET_KEY` | recommended | random per run | Signs login cookies. Without it everyone is logged out when the server restarts. Generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DB_PATH` | | `database.db` | SQLite file path |
| `HOST` | | `0.0.0.0` | Bind address (`127.0.0.1` = this machine only) |
| `PORT` | | `5000` | Port |
| `FLASK_DEBUG` | | off | `1` enables debug mode — never with `HOST=0.0.0.0` |

```env
# .env
GEMINI_API_KEY=your_gemini_api_key_here
```

> **Warning** Never commit `.env`. It is listed in `.gitignore` and contains your private API key.

> **Note** On the LAN the app is served over plain HTTP, so passwords travel unencrypted over Wi-Fi.
> Don't reuse a password from another service. Use HTTPS if you deploy it to the internet.

---

##  API Reference

All endpoints except `/api/auth/*` require login and return `401` otherwise.
Every query is scoped to the logged-in user.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Create an account (username, password, age group, income group) and log in |
| `POST` | `/api/auth/login` | Log in |
| `POST` | `/api/auth/logout` | Log out |
| `GET` | `/api/auth/me` | Current user (`401` when logged out) |
| `PUT` | `/api/budget` | Set or clear the monthly budget (`{"monthly_budget": 500000}` or `null`) |
| `POST` | `/api/parse` | Parse one SMS → transaction data (preview only, does **not** save) |
| `POST` | `/api/parse/batch` | Parse many SMS at once in a single Gemini call (preview only) |
| `POST` | `/api/transactions` | Save a parsed transaction |
| `PUT` | `/api/transactions/<id>` | Edit a saved transaction |
| `DELETE` | `/api/transactions/<id>` | Delete a saved transaction (`404` if the id does not exist) |
| `GET` | `/api/transactions` | Fetch transaction history (`?month=YYYY-MM&category=&search=`) |
| `GET` | `/api/stats` | Monthly and category-level spending stats (`?month=YYYY-MM`) |
| `GET` | `/api/analysis` | Peer comparison + Gemini-generated advice (`?month=&age_group=&income_group=`, defaults to your profile) |

<details>
<summary><b>Response examples</b></summary>

#### `POST /api/parse`
```json
{
  "success": true,
  "data": {
    "amount": 12000,
    "store": "스타벅스",
    "category": "cafe",
    "date": "2026-07-14",
    "time": "14:32",
    "card": "신한카드"
  }
}
```

#### `POST /api/parse/batch`
```json
{
  "success": true,
  "data": [
    { "amount": 12000, "store": "스타벅스", "category": "cafe", "date": "2026-10-31", "time": "09:12", "card": "신한카드" },
    { "amount": 8500, "store": "김밥천국", "category": "food", "date": "2026-10-31", "time": "12:10", "card": "KB국민카드" }
  ],
  "skipped": 0
}
```

#### `GET /api/analysis`
```json
{
  "success": true,
  "data": {
    "user_total": 352000,
    "peer_average": 298000,
    "peer_group": "20대초반 / mid-low",
    "has_peer_data": true,
    "by_category": {
      "cafe": { "user": 45000, "peer_avg": 32000 }
    },
    "advice": "Your cafe spending is 40% above the peer average this month. Cutting two visits a week could save you ₩13,000."
  }
}
```

</details>

---

##  Spending Categories

| Category | Key | Icon | Color |
|----------|-----|------|-------|
| Food | `food` | 🍽️ | `#FF6B6B` |
| Cafe | `cafe` | ☕ | `#C49A6C` |
| Transport | `transport` | 🚌 | `#4ECDC4` |
| Shopping | `shopping` | 🛍️ | `#9B59B6` |
| Medical | `medical` | 💊 | `#2ECC71` |
| Leisure | `leisure` | 🎬 | `#F39C12` |
| Other | `etc` | 📌 | `#95A5A6` |

---

##  Supported SMS Formats

The parser handles all major Korean card issuers out of the box.

```
[신한카드] 승인 12,000원 스타벅스 07/14 14:32 잔여한도 2,450,000원
[KB국민카드] 홍길동님 12,000원(일시불) 07/14 14:32 스타벅스 승인완료
삼성카드(1234) 12,000원 스타벅스 승인완료 07/14 14:32
[현대카드] 07/14 14:32 스타벅스 12,000원 승인 (일시불)
```

---

##  Authors

| Name | GitHub |
|------|--------|
| 박도연 (Doyeon Park) | [@Yyeon222](https://github.com/Yyeon222) |
| 이효재 (Hyojae Lee) | [@hyoj1226-ui](https://github.com/hyoj1226-ui) |

> Built as a team project at **서원고등학교** via GitHub Classroom.

---

##  License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

```
MIT License  Copyright (c) 2026 박도연, 이효재
```
