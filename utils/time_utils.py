from datetime import datetime
from zoneinfo import ZoneInfo

def now_kst() -> datetime:
    """현재 한국 시간을 반환합니다."""
    kst = datetime.now(ZoneInfo("Asia/Seoul"))
    return kst.replace(tzinfo=None)