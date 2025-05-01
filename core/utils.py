from datetime import datetime
from zoneinfo import ZoneInfo
from .config import Settings

def now_kst() -> datetime:
    return datetime.now(tz=ZoneInfo("Asia/Seoul"))