import pytest, httpx

from src.service_health_checker.models import CheckResult
from src.service_health_checker.make_http_request import make_http_request

client = httpx.AsyncClient()

async def test_make_http_request(httpx_mock):
    service = "example.com"
    url = "https://example.com"

    httpx_mock.add_response(
        json={"message": "Success"},
        status_code=200
    )

    response = await make_http_request(client, service, url)
        
    assert isinstance(response, CheckResult)
    assert response.check_type == "http"
    assert response.success == True
    assert response.duration >= 0


async def test_make_http_request_service_only(httpx_mock):
    service = "example.com"

    httpx_mock.add_response(
        json={"message": "Success"},
        status_code=200
    )

    response = await make_http_request(client, service, "")
    assert isinstance(response, CheckResult)
    assert response.check_type == "http"
    assert response.success == True
    assert response.duration >= 0


async def test_make_http_request_service_healthurl_empty():
    with pytest.raises(
        ValueError, 
        match="Host/health URL is required for HTTP check."
    ) as failed_http_check:
        result = await make_http_request(client, "", "")

    assert str(failed_http_check.value) == "Host/health URL is required for HTTP check."


async def test_make_http_request_service_invalid_healthurl():
    with pytest.raises(
        ValueError, 
        match="HealthURL is not a valid URI"
    ) as failed_http_check:
        result = await make_http_request(client, "example.com", "example.com")

    assert str(failed_http_check.value) == "HealthURL is not a valid URI"


async def test_make_http_request_404(httpx_mock):
    url = "https://example.com"

    httpx_mock.add_response(
        json={"message": "Not found"},
        status_code=404
    )

    result = await make_http_request(client, "example", url)
    assert isinstance(result, CheckResult)
    assert result.check_type == "http"
    assert result.success == False
    assert result.duration >= 0
    if result.details is not None:
        assert result.details["status_code"] == 404


async def test_make_http_request_500(httpx_mock):
    url = "https://example.com"

    httpx_mock.add_response(
        json={"message": "Internal server error"},
        status_code=500
    )

    result = await make_http_request(client, "example", url)
    assert isinstance(result, CheckResult)
    assert result.check_type == "http"
    assert result.success == False
    assert result.duration >= 0
    if result.details is not None:
        assert result.details["status_code"] == 500
        