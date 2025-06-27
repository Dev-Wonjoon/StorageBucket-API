from datetime import datetime
from zoneinfo import ZoneInfo
import uuid


def now_kst() -> datetime:
    """현재 한국 시간을 반환합니다."""
    kst = datetime.now(ZoneInfo("Asia/Seoul"))
    return kst.replace(tzinfo=None)


def uuid_generator() -> str:
    """uuid hex 8글자를 반환합니다."""
    uid = uuid.uuid4().hex[:8]
    return uid