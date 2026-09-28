import socket, pytest

from src.service_health_checker.dns_check import check_dns
from src.service_health_checker.models import CheckResult

def test_check_dns_with_monkeypatch(monkeypatch):
    def mock_gethostbyname(hostname):
        return "127.0.0.1"

    monkeypatch.setattr(socket, "gethostbyname", mock_gethostbyname)

    result = check_dns("example.com")
    assert isinstance(result, CheckResult)
    assert result.check_type == "dns"
    assert result.success == True
    assert result.duration
    if result.details is not None:
        assert result.details['ip_address'] == "127.0.0.1"

def test_failed_check_dns_with_monkeypatch(monkeypatch):
    def mock_failed_gethostbyname(hostname):
        raise socket.gaierror("Socket error: [Errno 11001] getaddrinfo failed")

    monkeypatch.setattr(socket, "gethostbyname", mock_failed_gethostbyname)

    result = check_dns("example.com")
    assert isinstance(result, CheckResult)
    assert result.check_type == "dns"
    assert result.success == False

def test_check_dns_empty_service():
    with pytest.raises(
        ValueError, 
        match="Hostname is required"
    ) as failed_dns_check:
        result = check_dns("")

    assert str(failed_dns_check.value) == "Hostname is required"

    