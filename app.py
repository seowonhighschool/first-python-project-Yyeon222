from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()  

import database
import gemini_parser

load_dotenv()

app = Flask(__name__)
CORS(app)

database.init_db()
@app.route('/')
def index():
    return render_template('index.html')

# ── SMS 파싱 ──────────────────────────────────────────
@app.route('/api/parse', methods=['POST'])
def parse_sms():
    try:
        data = request.get_json()
        if not data or 'sms' not in data:
            return jsonify({"success": False, "error": "sms 필드가 없습니다"}), 400

        result = gemini_parser.parse_sms(data['sms'])
        if not result['success']:
            return jsonify(result), 500

        # DB 저장
        d = result['data']
        transaction_id = database.insert_transaction(
            amount=d['amount'],
            store=d['store'],
            category=d['category'],
            date=d['date'],
            time=d['time'],
            card=d.get('card')
        )
        result['data']['id'] = transaction_id
        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── 거래 내역 조회 ────────────────────────────────────
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        month = request.args.get('month')
        rows = database.get_transactions(month)
        return jsonify({"success": True, "data": rows, "total": len(rows)})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── 대시보드 통계 ─────────────────────────────────────
@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        month = request.args.get('month')
        if not month:
            from datetime import datetime
            month = datetime.now().strftime('%Y-%m')

        stats = database.get_stats(month)
        return jsonify({"success": True, "data": stats})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── AI 분석 & 또래 비교 ───────────────────────────────
@app.route('/api/analysis', methods=['GET'])
def get_analysis():
    try:
        from datetime import datetime
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))

        stats = database.get_stats(month)
        peer = database.get_peer_averages()

        by_category = {}
        for cat, user_amt in stats['by_category'].items():
            by_category[cat] = {
                "user": user_amt,
                "peer_avg": peer.get(cat, 0)
            }

        peer_total = sum(peer.values())

        # Gemini 조언 생성
        advice = _generate_advice(stats['by_category'], peer)

        return jsonify({
            "success": True,
            "data": {
                "user_total": stats['total_amount'],
                "peer_average": peer_total,
                "peer_group": "20대 대학생",
                "by_category": by_category,
                "advice": advice
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _generate_advice(user_by_category, peer):
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        summary = "\n".join([
            f"- {cat}: 내 지출 {user_by_category.get(cat, 0)}원 / 또래 평균 {peer.get(cat, 0)}원"
            for cat in user_by_category
        ])

        prompt = f"""아래는 이번 달 소비 내역과 또래 평균 비교야.
{summary}

이 데이터를 바탕으로 2~3문장으로 맞춤형 소비 조언을 한국어로 작성해줘.
구체적인 절약 금액이나 횟수를 포함해서 실용적으로 써줘."""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text.strip()

    except Exception:
        return "데이터를 분석할 수 없습니다. 잠시 후 다시 시도해주세요."


if __name__ == '__main__':
    app.run(debug=True)
