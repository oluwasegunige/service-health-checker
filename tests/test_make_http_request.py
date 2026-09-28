import pytest

from src.service_health_checker.models import CheckResult
from src.service_health_checker.make_http_request import make_http_request

def test_make_http_request(requests_mock):
    url = "https://example.com"
    requests_mock.get(url, status_code=200)

    result = make_http_request("example", url)
    assert isinstance(result, CheckResult)
    assert result.check_type == "http"
    assert result.success == True
    assert result.duration >= 0


def test_make_http_request_service_only(requests_mock):
    service = "example.com"
    url = "https://" + service
    requests_mock.get(url, status_code=200)

    result = make_http_request("example", url)
    assert isinstance(result, CheckResult)
    assert result.check_type == "http"
    assert result.success == True
    assert result.duration >= 0


def test_make_http_request_service_healthurl_empty():
    with pytest.raises(
        ValueError, 
        match="Service/health URL is required for HTTP check."
    ) as failed_http_check:
        result = make_http_request("", "")

    assert str(failed_http_check.value) == "Service/health URL is required for HTTP check."


def test_make_http_request_404(requests_mock):
    url = "https://example.com"
    status_code = 404
    requests_mock.get(url, status_code=status_code)

    result = make_http_request("example", url)
    assert isinstance(result, CheckResult)
    assert result.check_type == "http"
    assert result.success == False
    assert result.duration >= 0
    if result.details is not None:
        assert result.details["status_code"] == status_code


def test_make_http_request_500(requests_mock):
    url = "https://example.com"
    status_code = 500
    requests_mock.get(url, status_code=status_code)

    result = make_http_request("example", url)
    assert isinstance(result, CheckResult)
    assert result.check_type == "http"
    assert result.success == False
    assert result.duration >= 0
    if result.details is not None:
        assert result.details["status_code"] == status_code