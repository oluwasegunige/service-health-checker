import pytest, httpx, typer

from src.service_health_checker.health_check import get_delay, healthcheck, monitor_all, healthcheck_orchestrator
from src.service_health_checker.models import CheckResult
from src.service_health_checker.config import ServiceConfig

# get_delay() tests

def test_get_delay_x_2(monkeypatch):
    x = 2
    delay = 2 ** x
    monkeypatch.setattr("src.service_health_checker.health_check.random.randint", lambda a, b: 3)
    assert get_delay(x) >= 1 and get_delay(x) <= delay


def test_get_delay_x_4(monkeypatch):
    x = 4
    monkeypatch.setattr("src.service_health_checker.health_check.random.randint", lambda a, b: 6)
    assert get_delay(x) >= 1 and get_delay(x) <= 10


# monitor_all() tests

async def test_monitor_all_with_no_services(mocker):
    mock_healthcheck_orchestrator = mocker.patch(
        "src.service_health_checker.health_check.healthcheck_orchestrator")
    
    await monitor_all([])

    mock_healthcheck_orchestrator.assert_not_awaited()


async def test_monitor_all_monitors_single_service(mocker):
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_healthcheck_orchestrator = mocker.patch(
        "src.service_health_checker.health_check.healthcheck_orchestrator")
    
    await monitor_all([service])

    mock_healthcheck_orchestrator.assert_awaited_once()

    client, passed_service = mock_healthcheck_orchestrator.await_args.args

    assert passed_service == service
    assert isinstance(client, httpx.AsyncClient)


async def test_monitor_all_monitors_all_services(mocker):
    services = [
        ServiceConfig(
            host="example.com", 
            port=443, 
            timeout=3, 
            healthurl="https://example.com", 
            retries=2
        ),
        ServiceConfig(
            host="example2.com", 
            port=443, 
            timeout=3, 
            healthurl="https://example2.com", 
            retries=2
        ),
        ServiceConfig(
            host="example1.com", 
            port=443, 
            timeout=3, 
            healthurl="https://example1.com", 
            retries=2
        )
    ]

    mock_healthcheck_orchestrator = mocker.patch(
        "src.service_health_checker.health_check.healthcheck_orchestrator"
    )

    await monitor_all(services=services)

    assert mock_healthcheck_orchestrator.await_count == len(services)

    passed_services = [
        call.args[1]
        for call in mock_healthcheck_orchestrator.await_args_list
    ]

    assert passed_services == services


async def test_monitor_all_shares_http_client(mocker):
    services = [
        ServiceConfig(
            host="example.com", 
            port=443, 
            timeout=3, 
            healthurl="https://example.com", 
            retries=2
        ),
        ServiceConfig(
            host="example2.com", 
            port=443, 
            timeout=3, 
            healthurl="https://example2.com", 
            retries=2
        ),
        ServiceConfig(
            host="example1.com", 
            port=443, 
            timeout=3, 
            healthurl="https://example1.com", 
            retries=2
        )
    ]

    mock_healthcheck_orchestrator = mocker.patch(
        "src.service_health_checker.health_check.healthcheck_orchestrator"
    )

    await monitor_all(services=services)

    clients = [
        call.args[0]
        for call in mock_healthcheck_orchestrator.await_args_list
    ]

    assert len(clients) == len(services)
    assert clients[0] is clients[1]
    assert clients[1] is clients[2]


# healthcheck_orchestrator() tests

async def test_healthcheck_orchestrator_host_empty():
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )
    with pytest.raises(ValueError) as failed_healthcheck_orchestrator:
        result = await healthcheck_orchestrator(client=client, service=service)

    assert str(failed_healthcheck_orchestrator.value) == "Host cannot be empty"


async def test_healthcheck_orchestrator_port_0():
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=0, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )
    with pytest.raises(ValueError) as failed_healthcheck_orchestrator:
        result = await healthcheck_orchestrator(client=client, service=service)

    assert str(failed_healthcheck_orchestrator.value) == "Port must be an integer in the valid TCP port range (1–65535)"


async def test_healthcheck_orchestrator_port_neg1():
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=-1, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )
    with pytest.raises(ValueError) as failed_healthcheck_orchestrator:
        result = await healthcheck_orchestrator(client=client, service=service)

    assert str(failed_healthcheck_orchestrator.value) == "Port must be an integer in the valid TCP port range (1–65535)"


async def test_healthcheck_orchestrator_port_65536():
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=65536, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )
    with pytest.raises(ValueError) as failed_healthcheck_orchestrator:
        result = await healthcheck_orchestrator(client=client, service=service)

    assert str(failed_healthcheck_orchestrator.value) == "Port must be an integer in the valid TCP port range (1–65535)"


async def test_healthcheck_orchestrator_timeout_0():
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=0, 
        healthurl="https://example.com", 
        retries=2
    )
    with pytest.raises(ValueError) as failed_healthcheck_orchestrator:
        result = await healthcheck_orchestrator(client=client, service=service)

    assert str(failed_healthcheck_orchestrator.value) == "Timeout must be greater than zero"


async def test_healthcheck_orchestrator_timeout_lt0():
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=-1, 
        healthurl="https://example.com", 
        retries=2
    )
    with pytest.raises(ValueError) as failed_healthcheck_orchestrator:
        result = await healthcheck_orchestrator(client=client, service=service)

    assert str(failed_healthcheck_orchestrator.value) == "Timeout must be greater than zero"


async def test_healthcheck_orchestrator_retries_lt0():
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=-2
    )

    with pytest.raises(ValueError) as failed_healthcheck_orchestrator:
        result = await healthcheck_orchestrator(client=client, service=service)

    assert str(failed_healthcheck_orchestrator.value) == "Retries must be a non-negative number"


async def test_healthcheck_orchestrator_all_checks_pass(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

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
    
    success_healthcheck_orchestrator = await healthcheck_orchestrator(
        client=client, service=service
    )

    mock_dns_check.assert_awaited_once_with(host=service.host)
    mock_check_tcp_connection.assert_called_once_with(
        host=service.host, port=service.port, timeout=service.timeout
    )
    mock_make_http_request.assert_awaited_once_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    mock_sleep.assert_not_called()


async def test_healthcheck_orchestrator_dns_fail_once(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        side_effect=[
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=True, duration=0.01)])

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))
    
    orchestrator = await healthcheck_orchestrator(
        client=client, service=service
    )

    assert mock_dns_check.call_count == 2
    mock_get_delay.assert_called_once_with(0)
    mock_sleep.assert_called_once()
    mock_check_tcp_connection.assert_called()
    mock_make_http_request.assert_awaited()


async def test_healthcheck_orchestrator_dns_fail_every_time(mocker):
    retries = 2

    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=retries
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        side_effect=[
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=False, duration=0.01)
        ]
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    assert mock_dns_check.call_count == retries + 1
    assert mock_get_delay.call_count == retries
    assert mock_sleep.call_count == retries
    mock_check_tcp_connection.assert_called()
    mock_make_http_request.assert_awaited()
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_dns_fail_until_final_retry(mocker):
    retries = 3
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=retries
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        side_effect=[
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=False, duration=0.01), 
            CheckResult(check_type="dns", success=True, duration=0.01)])

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))
    
    orchestrator = await healthcheck_orchestrator(
        client=client, service=service
    )

    assert mock_dns_check.call_count == retries + 1
    assert mock_get_delay.call_count == retries
    assert mock_sleep.call_count == retries
    mock_check_tcp_connection.assert_called()
    mock_make_http_request.assert_awaited()


async def test_healthcheck_orchestrator_tcp_fail_once(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        side_effect=[
            CheckResult(check_type="tcp", success=False, duration=0.19), 
            CheckResult(check_type="tcp", success=True, duration=0.19)
        ]
    )

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))
    
    orchestrator = await healthcheck_orchestrator(
        client=client, service=service
    )

    mock_dns_check.assert_awaited()
    assert mock_check_tcp_connection.call_count == 2
    mock_get_delay.assert_called_once_with(0)
    mock_sleep.assert_called_once()
    mock_make_http_request.assert_awaited()


async def test_healthcheck_orchestrator_tcp_fail_every_time(mocker):
    retries = 2

    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=retries
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01))

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        side_effect=[
            CheckResult(check_type="tcp", success=False, duration=0.19), 
            CheckResult(check_type="tcp", success=False, duration=0.19), 
            CheckResult(check_type="tcp", success=False, duration=0.19)
        ]
    )

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    assert mock_check_tcp_connection.call_count == retries + 1
    assert mock_get_delay.call_count == retries
    assert mock_sleep.call_count == retries
    mock_make_http_request.assert_awaited()
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_tcp_fail_until_final_retry(mocker):
    retries = 3
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=retries
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        side_effect=[
            CheckResult(check_type="tcp", success=False, duration=0.19), 
            CheckResult(check_type="tcp", success=False, duration=0.19), 
            CheckResult(check_type="tcp", success=False, duration=0.19), 
            CheckResult(check_type="tcp", success=True, duration=0.19)
        ]
    )

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5))
    
    orchestrator = await healthcheck_orchestrator(
        client=client, service=service
    )

    mock_dns_check.assert_called()
    assert mock_check_tcp_connection.call_count == retries + 1
    assert mock_get_delay.call_count == retries
    assert mock_sleep.call_count == retries
    mock_make_http_request.assert_awaited()


async def test_healthcheck_orchestrator_http_500_once(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        side_effect=[
            CheckResult(
                check_type="http", 
                success=False, 
                duration=1.5, 
                details={"status_code": 500}
            ), 
            CheckResult(check_type="http", success=True, duration=1.5)
        ]
    )
    
    orchestrator = await healthcheck_orchestrator(
        client=client, service=service
    )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    mock_get_delay.assert_called_once_with(0)
    mock_sleep.assert_called_once()
    assert mock_make_http_request.call_count == 2
    mock_make_http_request.assert_awaited_with(
        client=client, host=service.host, healthurl=service.healthurl
    )


async def test_healthcheck_orchestrator_http_503_twice_before_success(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        side_effect=[
            CheckResult(
                check_type="http", 
                success=False, 
                duration=1.5, 
                details={"status_code": 503}
            ), 
            CheckResult(
                check_type="http", 
                success=False, 
                duration=1.5, 
                details={"status_code": 503}
            ), 
            CheckResult(check_type="http", success=True, duration=1.5)
        ]
    )
    
    orchestrator = await healthcheck_orchestrator(
        client=client, service=service
    )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    assert mock_get_delay.call_count == 2
    assert mock_sleep.call_count == 2
    assert mock_make_http_request.call_count == 3
    mock_make_http_request.assert_awaited_with(
        client=client, host=service.host, healthurl=service.healthurl
    )


async def test_healthcheck_orchestrator_http_500_every_time(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        side_effect=[
            CheckResult(
                check_type="http", 
                success=False, 
                duration=1.5, 
                details={"status_code": 500}
            ), 
            CheckResult(
                check_type="http", 
                success=False, 
                duration=1.5, 
                details={"status_code": 500}
            ), 
            CheckResult(
                check_type="http", 
                success=False, 
                duration=1.5, 
                details={"status_code": 500}
            ), 
        ]
    )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    assert mock_get_delay.call_count == 2
    assert mock_sleep.call_count == 2
    assert mock_make_http_request.call_count == 3
    mock_make_http_request.assert_awaited_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_http_400(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", 
            success=False, 
            duration=1.5, 
            details={"status_code": 400}
        )
    )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    mock_make_http_request.assert_awaited_once_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_http_401(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", 
            success=False, 
            duration=1.5, 
            details={"status_code": 401}
        )
    )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    mock_make_http_request.assert_awaited_once_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_http_404(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", 
            success=False, 
            duration=1.5, 
            details={"status_code": 404}
        )
    )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    mock_make_http_request.assert_awaited_once_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_http_499(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", 
            success=False, 
            duration=1.5, 
            details={"status_code": 499}
        )
    )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    mock_make_http_request.assert_awaited_once_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_http_details_none(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=2
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19))

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", 
            success=False, 
            duration=1.5
        )
    )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    mock_make_http_request.assert_awaited_once_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_dns_fail_retries_0(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=0
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=False, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=True, duration=0.19)
        )

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5)
        )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited_once_with(host=service.host)
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    mock_check_tcp_connection.assert_called()
    mock_make_http_request.assert_awaited()
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_tcp_fail_retries_0(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=0
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=False, duration=0.19)
        )

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", success=True, duration=1.5)
        )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once_with(
        host=service.host, port=service.port, timeout=service.timeout
    )
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    mock_make_http_request.assert_awaited()
    assert orchestrator.value.exit_code == 1


async def test_healthcheck_orchestrator_http_500_retries_0(mocker):
    client = httpx.AsyncClient()
    service = ServiceConfig(
        host="example.com", 
        port=443, 
        timeout=3, 
        healthurl="https://example.com", 
        retries=0
    )

    mock_sleep = mocker.patch("time.sleep")

    mock_get_delay = mocker.patch(
        "src.service_health_checker.health_check.get_delay"
    )

    mock_dns_check = mocker.patch(
        "src.service_health_checker.health_check.check_dns",
        return_value=CheckResult(
            check_type="dns", success=True, duration=0.01
        )
    )

    mock_check_tcp_connection = mocker.patch(
        "src.service_health_checker.health_check.check_tcp_connection",
        return_value=CheckResult(
            check_type="tcp", success=False, duration=0.19
        )
    )

    mock_make_http_request = mocker.patch(
        "src.service_health_checker.health_check.make_http_request",
        return_value=CheckResult(
            check_type="http", 
            success=False, 
            duration=1.5, 
            details={"status_code": 500}
        )
    )
    
    with pytest.raises(typer.Exit) as orchestrator:
        await healthcheck_orchestrator(
            client=client, service=service
        )

    mock_dns_check.assert_awaited()
    mock_check_tcp_connection.assert_called_once()
    mock_make_http_request.assert_awaited_once_with(
        client=client, host=service.host, healthurl=service.healthurl
    )
    mock_get_delay.assert_not_called()
    mock_sleep.assert_not_called()
    assert orchestrator.value.exit_code == 1

