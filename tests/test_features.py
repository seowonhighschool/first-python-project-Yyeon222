# tests/test_features.py
# 거래 수정, 여러 건 붙여넣기, 월 예산을 검사한다. Gemini는 conftest의 가짜로 대체한다.
import json

import pytest

import app as app_module
import database
from conftest import signup

SAMPLE = {
    "amount": 12000,
    "store": "스타벅스",
    "category": "cafe",
    "date": "2026-07-14",
    "time": "14:32",
    "card": "신한카드",
}


def save(client, **overrides):
    return client.post("/api/transactions", json={**SAMPLE, **overrides}).get_json()["data"]["id"]


# ── 거래 수정 (PUT /api/transactions/<id>) ───────────
def test_update_changes_transaction_and_stats(client):
    tid = save(client)

    res = client.put(f"/api/transactions/{tid}", json={**SAMPLE, "category": "food", "amount": "15,000"})

    assert res.status_code == 200
    assert res.get_json()["data"]["amount"] == 15000
    row = client.get("/api/transactions").get_json()["data"][0]
    assert (row["category"], row["amount"]) == ("food", 15000)

    by_category = client.get("/api/stats?month=2026-07").get_json()["data"]["by_category"]
    assert by_category["food"] == 15000
    assert by_category["cafe"] == 0


@pytest.mark.parametrize("overrides", [
    {"category": "travel"},
    {"amount": "abc"},
    {"amount": 0},
    {"store": ""},
])
def test_update_validation_is_400(client, overrides):
    tid = save(client)
    assert client.put(f"/api/transactions/{tid}", json={**SAMPLE, **overrides}).status_code == 400


def test_update_unknown_or_others_transaction_is_404(make_client):
    alice, bob = make_client(), make_client()
    signup(alice, username="alice")
    signup(bob, username="bob")
    tid = save(alice)

    assert bob.put(f"/api/transactions/{tid}", json={**SAMPLE, "amount": 1}).status_code == 404
    assert alice.put("/api/transactions/99999", json=SAMPLE).status_code == 404
    # bob이 고치려 했어도 alice의 거래는 그대로다
    assert alice.get("/api/transactions").get_json()["data"][0]["amount"] == 12000


def test_update_requires_login(anon_client):
    assert anon_client.put("/api/transactions/1", json=SAMPLE).status_code == 401


# ── 여러 건 붙여넣기 (POST /api/parse/batch) ─────────
def batch_reply(*items):
    return "```json\n" + json.dumps(list(items), ensure_ascii=False) + "\n```"


def test_batch_parse_returns_all_items_without_saving(client, gemini_calls):
    gemini_calls.reply = batch_reply(
        {**SAMPLE, "amount": "12,000"},
        {**SAMPLE, "store": "김밥천국", "category": "snack", "amount": 8500},
    )

    res = client.post("/api/parse/batch", json={"sms": "문자1\n문자2"})

    assert res.status_code == 200
    body = res.get_json()
    assert [d["amount"] for d in body["data"]] == [12000, 8500]
    assert body["data"][1]["category"] == "etc"     # 7개 밖의 카테고리는 etc로 보정
    assert body["skipped"] == 0
    assert len(gemini_calls.prompts) == 1           # 여러 건이어도 Gemini는 한 번만
    assert client.get("/api/transactions").get_json()["total"] == 0   # 미리보기 전용


def test_batch_parse_skips_unreadable_items(client, gemini_calls):
    gemini_calls.reply = batch_reply(SAMPLE, {**SAMPLE, "store": ""}, "이상한 값")

    body = client.post("/api/parse/batch", json={"sms": "문자들"}).get_json()

    assert len(body["data"]) == 1
    assert body["skipped"] == 2


def test_batch_parse_accepts_single_object_reply(client, gemini_calls):
    gemini_calls.reply = json.dumps(SAMPLE, ensure_ascii=False)
    assert len(client.post("/api/parse/batch", json={"sms": "문자"}).get_json()["data"]) == 1


def test_batch_parse_caps_item_count(client, gemini_calls, monkeypatch):
    monkeypatch.setattr(app_module.gemini_parser, "MAX_BATCH_ITEMS", 3)
    gemini_calls.reply = batch_reply(*[SAMPLE] * 5)
    assert len(client.post("/api/parse/batch", json={"sms": "문자"}).get_json()["data"]) == 3


@pytest.mark.parametrize("reply", ["[]", "결제 문자가 없어요", '{"amount": null}'])
def test_batch_parse_nothing_readable_is_400(client, gemini_calls, reply):
    gemini_calls.reply = reply
    res = client.post("/api/parse/batch", json={"sms": "광고 문자"})
    assert res.status_code == 400
    assert res.get_json()["success"] is False


def test_batch_parse_rejects_too_long_input_before_gemini(client, gemini_calls):
    sms = "가" * (app_module.MAX_BATCH_SMS_LENGTH + 1)
    assert client.post("/api/parse/batch", json={"sms": sms}).status_code == 400
    assert not gemini_calls.prompts


def test_batch_parse_requires_login(anon_client, gemini_calls):
    assert anon_client.post("/api/parse/batch", json={"sms": "x"}).status_code == 401
    assert not gemini_calls.prompts


# ── 월 예산 (PUT /api/budget) ────────────────────────
def test_budget_set_and_clear(client):
    res = client.put("/api/budget", json={"monthly_budget": 500000})
    assert res.status_code == 200
    assert res.get_json()["data"]["monthly_budget"] == 500000
    assert client.get("/api/auth/me").get_json()["data"]["monthly_budget"] == 500000

    res = client.put("/api/budget", json={"monthly_budget": None})
    assert res.get_json()["data"]["monthly_budget"] is None


@pytest.mark.parametrize("payload", [
    {},
    {"monthly_budget": 0},
    {"monthly_budget": -1000},
    {"monthly_budget": "500000"},
    {"monthly_budget": 1.5},
    {"monthly_budget": True},
    {"monthly_budget": app_module.MAX_MONTHLY_BUDGET + 1},
])
def test_budget_validation_is_400(client, payload):
    assert client.put("/api/budget", json=payload).status_code == 400


def test_budget_is_per_user(make_client):
    alice, bob = make_client(), make_client()
    signup(alice, username="alice")
    signup(bob, username="bob")

    alice.put("/api/budget", json={"monthly_budget": 300000})
    assert bob.get("/api/auth/me").get_json()["data"]["monthly_budget"] is None


def test_budget_requires_login(anon_client):
    assert anon_client.put("/api/budget", json={"monthly_budget": 1000}).status_code == 401


def test_migration_adds_monthly_budget(tmp_path, monkeypatch):
    # 예산 기능 전에 만든 users 테이블 (로그인 도입 직후 스키마)
    db_path = str(tmp_path / "old.db")
    monkeypatch.setattr(database, "DB_PATH", db_path)
    conn = database.get_connection()
    conn.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL, age_group TEXT NOT NULL, income_group TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        );
        INSERT INTO users (username, password_hash, age_group, income_group)
        VALUES ('old', 'x', '20대초반', 'mid-low');
    """)
    conn.close()

    database.init_db()

    user = database.get_user_with_password("old")
    assert user["monthly_budget"] is None
