from datetime import datetime
from zoneinfo import ZoneInfo
import uuid, re, unicodedata


_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')   # Windows + POSIX reserved
_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"{x}{i}" for x in ("COM", "LPT") for i in range(1, 10)),
}


def now_kst() -> datetime:
    """현재 한국 시간을 반환합니다."""
    kst = datetime.now(ZoneInfo("Asia/Seoul"))
    return kst.replace(tzinfo=None)


def uuid_generator() -> str:
    """uuid hex 8글자를 반환합니다."""
    uid = uuid.uuid4().hex[:8]
    return uid


def safe_string(s: str, *, replacement: str = "_", allow_unicode: bool = True, max_length: int = 255) -> str:
    """
    파일·폴더 이름으로 안전하게 변환한 문자열을 반환한다.

    Parameters
    ----------
    s : str
        원본 문자열
    replacement : str, default "_"
        제거된 문자 대신 넣을 문자
    max_length : int, default 255
        최종 문자열 최대 길이
    allow_unicode : bool, default True
        False 로 주면 NFC → ASCII 로 NFKD 변환 후 비ASCII 삭제

    Returns
    -------
    str
        파일 시스템 안전 문자열
    """
    
    if allow_unicode:
        s = unicodedata.normalize("NFC", s)
    else:
        s = (
            unicodedata.normalize("NFKD", s)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        
    s = _INVALID_CHARS.sub(replacement, s)
    
    s = s.strip(" .")
    
    if s.upper() in _RESERVED_NAMES:
        s = f"_{s}_"
    
    return s[:max_length] or replacement