from google import genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_TEMPLATE = """
다음 카드 결제 문자에서 정보를 추출해줘.
반드시 아래 JSON 형식으로만 응답해. 다른 말은 절대 하지 마.

{{
  "amount": 숫자 (원 단위 정수, 쉼표 없이),
  "store": "상점명",
  "category": "food|cafe|transport|shopping|medical|leisure|etc 중 하나",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "card": "카드사명"
}}

SMS: {sms_text}
"""


def parse_sms(sms_text):
    try:
        prompt = PROMPT_TEMPLATE.format(sms_text=sms_text)
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt
        )

        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        parsed = json.loads(raw)
        parsed["amount"] = int(parsed["amount"])
        parsed.setdefault("category", "etc")

        return {"success": True, "data": parsed}

    except json.JSONDecodeError:
        return {"success": False, "error": "JSON 파싱 실패", "data": {"category": "etc"}}
    except Exception as e:
        return {"success": False, "error": str(e)}