import pytest, socket

from src.service_health_checker.models import CheckResult
from src.service_health_checker.check_tcp_connection import check_tcp_connection

class MockSocket:
    def __init__(self, *args, **kwargs):
        pass
    def settimeout(self, timeout):
        pass
    def connect(self, address):
        pass
    def close(self):
        pass


def test_check_tcp_connection_with_monkeypatch(monkeypatch):
    monkeypatch.setattr("socket.socket", MockSocket)

    result = check_tcp_connection("example.com", 80, 5)
    assert isinstance(result, CheckResult)
    assert result.check_type == "tcp"
    assert result.success == True
    assert result.duration >= 0


def test_check_tcp_connection_with_host_empty():
    with pytest.raises(
        ValueError, 
        match="Hostname is required"
    ) as failed_tcp_check:
        result = check_tcp_connection("", 80, 5)

    assert str(failed_tcp_check.value) == "Hostname is required"


def test_check_tcp_connection_with_port_0():
    with pytest.raises(
        ValueError, 
        match="Port must be greater than zero"
    ) as failed_tcp_check:
        result = check_tcp_connection("example.com", 0, 3)

    assert str(failed_tcp_check.value) == "Port must be greater than zero"


def test_check_tcp_connection_with_port_lte_0():
    with pytest.raises(
        ValueError, 
        match="Port must be greater than zero"
    ) as failed_tcp_check:
        result = check_tcp_connection("example.com", -80, 2)

    assert str(failed_tcp_check.value) == "Port must be greater than zero"


def test_check_tcp_connection_with_timeout_0():
    with pytest.raises(
        ValueError, 
        match="Timeout must be greater than zero"
    ) as failed_tcp_check:
        result = check_tcp_connection("example.com", 80, 0)

    assert str(failed_tcp_check.value) == "Timeout must be greater than zero"


def test_check_tcp_connection_with_timeout_lte_0():
    with pytest.raises(
        ValueError, 
        match="Timeout must be greater than zero"
    ) as failed_tcp_check:
        result = check_tcp_connection("example.com", 80, -2)

    assert str(failed_tcp_check.value) == "Timeout must be greater than zero"


def test_check_tcp_connection_with_monkeypatch_timeout_exceeded(monkeypatch):
    class MockSocketTimeout(MockSocket):
        def connect(self, address):
            raise socket.timeout("Socket timeout")

    monkeypatch.setattr("socket.socket", MockSocketTimeout)

    timeout = 5

    result = check_tcp_connection("example.com", 80, timeout)
    assert isinstance(result, CheckResult)
    assert result.check_type == "tcp"
    assert result.success == False
    assert result.duration == timeout
    assert result.error == f"Socket timeout after {timeout}s"


def test_check_tcp_connection_with_monkeypatch_error(monkeypatch):
    class MockSocketError(MockSocket):
        def connect(self, address):
            raise socket.error("Socket error")

    monkeypatch.setattr("socket.socket", MockSocketError)

    result = check_tcp_connection("example.com", 80, 5)
    assert isinstance(result, CheckResult)
    assert result.check_type == "tcp"
    assert result.success == False
    assert result.duration >= 0
    assert result.error == f"Socket error: Socket error"

    