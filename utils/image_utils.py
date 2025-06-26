from io import BytesIO
from typing import Optional

from PIL import Image


def convert_to_webp(
    data: bytes,
    *,
    quality: int = 100,
    method: int = 3,
    optimize: bool = True,
) -> Optional[bytes]:
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        buf = BytesIO()
        img.save(
            buf,
            format="WEBP",
            quality=quality,
            method=method,
            optimize=optimize
        )
        return buf.getvalue()
    except Exception:
        return None