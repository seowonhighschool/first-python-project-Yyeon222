from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

import database
import gemini_parser

load_dotenv()

app = Flask(__name__)
CORS(app)

database.init_db()

# POST /api/transactions 저장에 반드시 필요한 필드 (card는 없어도 허용)
REQUIRED_TRANSACTION_FIELDS = ['amount', 'store', 'category', 'date', 'time']


@app.route('/')
def index():
    return render_template('index.html')

# ── SMS 파싱 ──────────────────────────────────────────
# 파싱은 미리보기까지만 담당한다. 저장은 POST /api/transactions 하나로만 이뤄진다.
# (두 곳에서 저장하면 "분석하기" + "저장하기"로 같은 거래가 두 번 들어간다)
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


# ── 거래 저장 ─────────────────────────────────────────
@app.route('/api/transactions', methods=['POST'])
def save_transaction():
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"success": False, "error": "요청 본문이 비어있습니다"}), 400

        missing = [f for f in REQUIRED_TRANSACTION_FIELDS if not data.get(f)]
        if missing:
            return jsonify({
                "success": False,
                "error": f"필수 항목이 없습니다: {', '.join(missing)}"
            }), 400

        # DB 컬럼에 해당하는 키만 뽑는다 (id 등 불필요한 키가 섞여 들어오는 것을 막는다)
        transaction_id = database.insert_transaction({
            'amount':   data['amount'],
            'store':    data['store'],
            'category': data['category'],
            'date':     data['date'],
            'time':     data['time'],
            'card':     data.get('card'),
        })
        return jsonify({"success": True, "data": {"id": transaction_id}})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ── 거래 내역 조회 ────────────────────────────────────
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    try:
        month    = request.args.get('month')
        category = request.args.get('category')
        search   = request.args.get('search')

        rows = database.get_transactions(month, category, search)
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
        month      = request.args.get('month', datetime.now().strftime('%Y-%m'))
        age_group  = request.args.get('age_group', '20대초반')
        income_group = request.args.get('income_group', 'mid-low')

        stats = database.get_stats(month)
        peer  = database.get_peer_averages(age_group, income_group)

        by_category = {
            cat: {"user": user_amt, "peer_avg": peer.get(cat, 0)}
            for cat, user_amt in stats['by_category'].items()
        }

        peer_total = sum(peer.values())

        # 시드가 없거나 해당 그룹 조합이 없으면 peer가 {}로 온다.
        # 이때 또래 평균 0원을 그대로 보여주면 "내가 무한히 더 쓴다"처럼 오해되므로 구분해서 안내한다.
        if not peer:
            advice = (
                f"'{age_group} / {income_group}' 그룹의 또래 데이터가 없습니다. "
                "python seed.py 를 실행해 또래 비교 데이터를 채워주세요."
            )
        else:
            advice = _generate_advice(stats['by_category'], peer)

        return jsonify({
            "success": True,
            "data": {
                "user_total":    stats['total_amount'],
                "peer_average":  peer_total,
                "peer_group":    f"{age_group} / {income_group}",
                "has_peer_data": bool(peer),
                "by_category":   by_category,
                "advice":        advice
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _generate_advice(user_by_category, peer):
    try:
        summary = "\n".join([
            f"- {cat}: 내 지출 {user_by_category.get(cat, 0)}원 / 또래 평균 {peer.get(cat, 0)}원"
            for cat in user_by_category
        ])

        prompt = f"""아래는 이번 달 소비 내역과 또래 평균 비교야.
{summary}

이 데이터를 바탕으로 2~3문장으로 맞춤형 소비 조언을 한국어로 작성해줘.
구체적인 절약 금액이나 횟수를 포함해서 실용적으로 써줘."""

        # 모델명·클라이언트는 gemini_parser 한 곳에서만 관리한다
        return gemini_parser.generate_text(prompt)

    except Exception as e:
        # 통째로 삼키면 키 오류와 일시적 장애를 구분할 수 없어 원인을 서버 로그에 남긴다
        app.logger.warning("조언 생성 실패: %s", e)
        return "조언을 생성하지 못했습니다. 잠시 후 다시 시도해주세요."


if __name__ == '__main__':
    app.run(debug=True)
