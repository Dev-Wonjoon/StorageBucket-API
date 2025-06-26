from pathlib import Path
import importlib.resources as r
import tldextract

# 패키지 내부 파일 로드
_snapshot_path: Path = (
    r.files(__package__) / "public_suffix_list.dat"
    if r.is_resource(__package__, "public_suffix_list.dat")
    else None
)

suffix_list_urls = () if _snapshot_path else None

class DomainExtractor:
    
    def __init__(self, cache_dir: str | Path) -> None:
        cache_dir = Path(cache_dir).expanduser() / ".tld_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._extract = tldextract.TLDExtract(
            cache_dir=str(cache_dir),
            suffix_list_urls=suffix_list_urls,
            fallback_to_snapshot=bool(_snapshot_path),
            include_psl_private_domains=False,
        )
        

    def extract_domain(self, url: str) -> str:
        ext = self._extract(url)
        return ext.domain.lower()

    def extract_suffix(self, url: str) -> str:
        return self._extract(url).suffix.lower()

    def extract_subdomain(self, url: str) -> str:
        return self._extract(url).subdomain.lower()

    def extract_full_domain(self, url: str) -> str:
        ext = self._extract(url)
        
        return f"{ext.domain.lower()}.{ext.subdomain.lower()}"
    
    __call__ = extract_domain