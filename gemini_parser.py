from datetime import datetime
from functools import lru_cache
import json
import logging
import os
import re
import time

from google import genai
from dotenv import load_dotenv

import database

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Gemini 클라이언트 (지연 생성) ─────────────────────────────────────────────
# 모듈 최상단에서 Client를 만들면 GEMINI_API_KEY가 없을 때 import 자체가 터져서
# Flask 서버가 아예 뜨지 않는다. 키 확인은 실제 호출 시점으로 미룬다.
MODEL_NAME = "gemini-3.8-flash"

# 파싱 결과에 반드시 있어야 하는 필드 (card는 없어도 허용)
REQUIRED_FIELDS = ["amount", "store", "category", "date", "time"]

# Gemini가 간헐적으로 503(과부하)을 반환한다. 시연 중 실패로 보이지 않도록 재시도한다.
MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 1.5  # 초, 시도마다 2배씩 증가
RETRYABLE_STATUSES = (429, 500, 502, 503, 504)


@lru_cache(maxsize=1)
def _get_client():
    """클라이언트를 한 번만 만들어 재사용한다 (요청마다 새로 만들지 않는다)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY가 설정되지 않았습니다. .env 파일에 키를 넣어주세요."
        )
    return genai.Client(api_key=api_key)


PROMPT_TEMPLATE = """
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
"""


def _status_code(exc) -> int | None:
    """예외에서 HTTP 상태코드를 뽑아낸다. SDK 버전에 따라 속성명이 달라서 문자열도 본다."""
    for attr in ("code", "status_code"):
        value = getattr(exc, attr, None)
        if isinstance(value, int):
            return value

    match = re.search(r"\b([45]\d\d)\b", str(exc))
    return int(match.group(1)) if match else None


def generate_text(prompt: str) -> str:
    """
    일반 텍스트 생성. Gemini 호출을 이 모듈 하나로 모아 모델명이 갈라지지 않게 한다.
    일시적 오류(429/5xx)는 지수 백오프로 재시도한다.
    """
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = _get_client().models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            return response.text.strip()

        except Exception as e:
            status = _status_code(e)
            if status not in RETRYABLE_STATUSES or attempt == MAX_ATTEMPTS:
                raise

            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
            logger.warning(
                "Gemini 일시적 오류(%s). %.1f초 후 재시도 (%d/%d)",
                status, delay, attempt + 1, MAX_ATTEMPTS,
            )
            time.sleep(delay)

    # 도달하지 않는다 (마지막 시도는 위에서 raise된다)
    raise RuntimeError("Gemini 호출에 실패했습니다.")


def _strip_code_fence(raw: str) -> str:
    """```json ... ``` 형태로 감싸져 오면 펜스를 제거한다."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def to_int_amount(value) -> int:
    """
    '12,000' / '12000원' / 12000 모두 12000으로 정규화한다.
    음수 부호는 보존한다. 숫자만 남기면 -500이 조용히 500이 되어
    호출부의 검증을 그대로 통과해버린다.
    """
    text = str(value).strip()
    is_negative = text.startswith("-")

    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        raise ValueError(f"금액을 숫자로 변환할 수 없습니다: {value!r}")

    amount = int(digits)
    return -amount if is_negative else amount


def parse_sms(sms_text):
    try:
        # 프롬프트에 JSON 중괄호가 있어 str.format()은 KeyError를 낸다 → replace 사용
        today = datetime.now()
        prompt = (
            PROMPT_TEMPLATE
            .replace("{today}", today.strftime("%Y년 %m월 %d일"))
            .replace("{current_year}", str(today.year))
            .replace("{sms_text}", sms_text)
        )

        parsed = json.loads(_strip_code_fence(generate_text(prompt)))

        missing = [f for f in REQUIRED_FIELDS if not parsed.get(f)]
        if missing:
            return {
                "success": False,
                "error": f"문자에서 {', '.join(missing)} 항목을 읽지 못했습니다. 문자 내용을 확인해주세요.",
                "status": 400,
            }

        parsed["amount"] = to_int_amount(parsed["amount"])

        # 7개 고정 카테고리 외의 값이 들어오면 통계에서 조용히 누락되므로 etc로 보정
        if parsed.get("category") not in database.CATEGORIES:
            parsed["category"] = "etc"

        return {"success": True, "data": parsed}

    # status는 라우트가 HTTP 코드를 고르기 위한 내부 힌트다 (응답 본문에는 넣지 않는다).
    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Gemini 응답을 JSON으로 읽지 못했습니다.",
            "status": 400,
        }
    except ValueError as e:
        return {"success": False, "error": str(e), "status": 400}
    except RuntimeError as e:
        return {"success": False, "error": str(e), "status": 500}
    except Exception as e:
        status = _status_code(e)
        logger.warning("Gemini 호출 실패(%s): %s", status, e)

        if status in RETRYABLE_STATUSES:
            message = (
                f"Gemini 서버가 혼잡합니다. {MAX_ATTEMPTS}번 시도했지만 실패했어요. "
                "잠시 후 다시 시도해주세요."
            )
        else:
            message = f"Gemini 호출 실패: {e}"

        return {"success": False, "error": message, "status": 502}
