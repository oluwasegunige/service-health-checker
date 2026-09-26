import pytest

from src.service_health_checker.health_check import get_delay, healthcheck
from src.service_health_checker import health_check
from src.service_health_checker.dns_check import check_dns
from src.service_health_checker.models import CheckResult
from src.service_health_checker.logging_config import logger
from src.service_health_checker.config import load_config

def test_get_delay_x_2(monkeypatch):
    x = 2
    delay = 2 ** x
    monkeypatch.setattr("src.service_health_checker.health_check.random.randint", lambda a, b: 3)
    assert get_delay(x) >= 1 and get_delay(x) <= delay


def test_get_delay_x_4(monkeypatch):
    x = 4
    monkeypatch.setattr("src.service_health_checker.health_check.random.randint", lambda a, b: 6)
    assert get_delay(x) >= 1 and get_delay(x) <= 10


def test_health_check_happy(mocker):
    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01))

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))

    with pytest.raises(SystemExit) as health_check_happy:
        healthcheck(
            service="example.com", 
            port=80, 
            timeout=5, 
            healthurl="https://example.com")

    assert health_check_happy.value.code == 0
    mock_dns_check.assert_called_once_with(service="example.com")
    mock_check_tcp_connection.assert_called_once_with(
        host="example.com", port=80, timeout=5)
    mock_make_http_request.assert_called_once_with(
        service="example.com", healthurl="https://example.com")
