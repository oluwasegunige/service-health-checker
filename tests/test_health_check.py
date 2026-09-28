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

def test_health_check_dns_immediate_success(mocker):
    mock_sleep = mocker.patch("time.sleep")

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01))

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    with pytest.raises(SystemExit) as health_check_dns_immediate_success:
        healthcheck(
            service="example.com", 
            port=80, 
            timeout=5, 
            healthurl="https://example.com")

    assert health_check_dns_immediate_success.value.code == 0
    mock_dns_check.assert_called_once_with(service="example.com")
    mock_sleep.assert_not_called()
    mock_check_tcp_connection.assert_called()


def test_health_check_dns_fail_once(mocker):
    mock_sleep = mocker.patch("time.sleep")
    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay")

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        side_effect=[
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=True, duration=0.01)])

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    with pytest.raises(SystemExit) as health_check_dns_fail_once:
        healthcheck(
            service="example.com", 
            port=80, 
            timeout=5, 
            healthurl="https://example.com")

    assert health_check_dns_fail_once.value.code == 0
    assert mock_dns_check.call_count == 2
    mock_sleep.assert_called_once()
    mock_get_delay.assert_called_once()
    mock_check_tcp_connection.assert_called()
    

def test_health_check_dns_fail_thrice_default_max(mocker):
    mock_sleep = mocker.patch("time.sleep")
    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay")

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        side_effect=[
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=False, duration=0.01)])

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    with pytest.raises(SystemExit) as health_check_dns_fail_thrice_default_max:
        healthcheck(
            service="example.com", 
            port=80, 
            timeout=5, 
            healthurl="https://example.com")

    assert health_check_dns_fail_thrice_default_max.value.code == 1
    assert mock_dns_check.call_count == 3
    assert mock_sleep.call_count == 2
    assert mock_get_delay.call_count == 2
    mock_check_tcp_connection.assert_called()

def test_health_check_tcp_immediate_success(mocker):
    mock_sleep = mocker.patch("time.sleep")

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

    with pytest.raises(SystemExit) as health_check_tcp_immediate_success:
        healthcheck(
            service="example.com", 
            port=80, 
            timeout=5, 
            healthurl="https://example.com")

    assert health_check_tcp_immediate_success.value.code == 0
    mock_dns_check.assert_called()
    mock_check_tcp_connection.assert_called_once_with(service="example.com")
    mock_sleep.assert_not_called()
    mock_make_http_request.assert_called()


def test_health_check_tcp_fail_once(mocker):
    mock_sleep = mocker.patch("time.sleep")
    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay")

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01))

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        side_effect=[
            CheckResult(
                check_type="tcp", 
                success=False, 
                duration=3, 
                error="Socket timeout after 3s"), 
            CheckResult(check_type="tcp", success=True, duration=0.19)])

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))

    with pytest.raises(SystemExit) as health_check_tcp_fail_once:
        healthcheck(
            service="example.com", 
            port=80, 
            timeout=5, 
            healthurl="https://example.com")

    assert health_check_tcp_fail_once.value.code == 0
    mock_dns_check.assert_called()
    assert mock_check_tcp_connection.call_count == 2
    mock_sleep.assert_called_once()
    mock_get_delay.assert_called_once()
    mock_make_http_request.assert_called()
    

def test_health_check_tcp_fail_thrice_default_max(mocker):
    mock_sleep = mocker.patch("time.sleep")
    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay")

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01))

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        side_effect=[
            CheckResult(
                check_type="tcp", 
                success=False, 
                duration=3, 
                error="Socket timeout after 3s"),
            CheckResult(
                check_type="tcp", 
                success=False, 
                duration=3, 
                error="Socket timeout after 3s"),
            CheckResult(
                check_type="tcp", 
                success=False, 
                duration=3, 
                error="Socket timeout after 3s")])

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))

    with pytest.raises(SystemExit) as health_check_tcp_fail_thrice_default_max:
        healthcheck(
            service="example.com", 
            port=80, 
            timeout=5, 
            healthurl="https://example.com")

    assert health_check_tcp_fail_thrice_default_max.value.code == 1
    mock_dns_check.assert_called()
    assert mock_check_tcp_connection.call_count == 3
    assert mock_sleep.call_count == 2
    assert mock_get_delay.call_count == 2
    mock_make_http_request.assert_called()