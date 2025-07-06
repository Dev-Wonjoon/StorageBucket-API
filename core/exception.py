
class DuplicateUrlError(Exception):
    """이미 저장된 URL일 경우"""
    def __init__(self, url):
        msg = "이미 등록된 URL입니다."
        if url:
            mag += f"{url}"
        super().__init__(msg)
    

class PlatformNotFoundError(Exception):
    """지정된 PLATFORM_NAME이 없을 경우"""
    
    def __init__(self, platform_name: str):
        super().__init__(f"플랫폼 '{platform_name}'가 DB에 없습니다.")