from src.service_health_checker.is_valid_uri import is_valid_uri

def test_is_valid_uri_happy_http():
    result = is_valid_uri("http://example.com")
    assert result == True


def test_is_valid_uri_happy_https():
    result = is_valid_uri("https://example.com")
    assert result == True


def test_is_valid_uri_happy_ftp():
    result = is_valid_uri("ftp://://example.com")
    assert result == True


def test_is_valid_uri_happy_ip():
    result = is_valid_uri("http://192.168.1.1:8080")
    assert result == True


def test_is_valid_uri_no_scheme():
    result = is_valid_uri("://example.com")
    assert result == False


def test_is_valid_uri_no_host():
    result = is_valid_uri("https:///path/to/page")
    assert result == False


def test_is_valid_uri_relative_path():
    result = is_valid_uri("/just/a/path")
    assert result == False


def test_is_valid_uri_random_text():
    result = is_valid_uri("not-a-uri-at-all")
    assert result == False


def test_is_valid_uri_control_chars():
    result = is_valid_uri("https://example.com\n/path")
    assert result == False


def test_is_valid_uri_malformed_ipv4():
    result = is_valid_uri("http://[localhost]/")
    assert result == False


def test_is_valid_uri_backslash():
    result = is_valid_uri("https://example.com\at-bad-domain.com")
    assert result == False

