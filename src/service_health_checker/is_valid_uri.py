import unicodedata
from urllib.parse import urlparse

def is_valid_uri(uri_str: str) -> bool:
    """
    To validate a URI/URL
    """
    if "\\" in uri_str:
        return False
    
    if any(unicodedata.category(c).startswith('C') or c.isspace() for c in uri_str):
        return False
    
    try:
        result = urlparse(url=uri_str)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    