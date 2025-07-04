
class DuplicateUrlError(Exception):
    """이미 저장된 URL일 경우"""
    

class PlatformNotFoundError(Exception):
    """지정된 PLATFORM_NAME이 없을 경우"""