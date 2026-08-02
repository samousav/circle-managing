import os
import hmac
import hashlib
import urllib.parse
import json
from dotenv import load_dotenv
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def validate_telegram_data(initial_data: str) -> dict | None:
    if not initial_data:
        return None

    bot_token = os.getenv("BOT_TOKEN", "")

    parsed_data = dict(urllib.parse.parse_qsl(initial_data))

    if "hash" not in parsed_data:
        return None

    received_hash = parsed_data.pop("hash")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed_data.items()))

    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if calculated_hash == received_hash:
        user_json_string = parsed_data.get("user", "{}")
        return json.loads(user_json_string)

    return None