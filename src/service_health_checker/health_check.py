import typer, time, random, httpx, asyncio
from typing_extensions import Annotated
from pathlib import Path

from .logging_config import logger
from .dns_check import check_dns
from .check_tcp_connection import check_tcp_connection
from .make_http_request import make_http_request
from .config import load_config, ConfigError, ServiceConfig

def get_delay(x: int):
    delay = 2 ** x
    if delay >= 10:
        jittered_delay = random.randint(1, 10)
    else:
        jittered_delay = random.randint(1, delay)
    return jittered_delay

async def healthcheck_orchestrator(
        client: httpx.AsyncClient, service: ServiceConfig
) -> None:
    """Asynchronously checks a single web service with retries and timeout."""
    results = {}

    host = service.host
    port = service.port
    timeout = service.timeout
    retries = service.retries
    healthurl = service.healthurl

    if host == "":
        raise ValueError("Host cannot be empty")

    if port < 1 or port > 65535:
        raise ValueError("Port must be an integer in the valid TCP port range (1–65535)")
    
    if timeout <= 0:
        raise ValueError("Timeout must be greater than zero")

    if retries < 0:
        raise ValueError("Retries must be a non-negative number")

    dns_check = await check_dns(host=host)
    results["dns"] = dns_check.success
    if dns_check.success == True:
        logger.info(f"DNS check passed: {host} {dns_check.duration:.2f}s")
    else:
        logger.warning(f"DNS check failed: {host} {dns_check.duration:.2f}s {dns_check.error}")
        for x in range(retries):
            delay = get_delay(x)
            time.sleep(delay)
            
            dns_check = await check_dns(host=host)
            results["dns"] = dns_check.success
            if dns_check.success == True:
                logger.info(f"DNS check passed: {host} {dns_check.duration:.2f}s after {x+1} retries")
                break
            logger.warning(f"DNS check failed: {host} {dns_check.duration:.2f}s {dns_check.error} after {x+1} retries")

    tcp_check = check_tcp_connection(host=host, port=port, timeout=timeout)
    results["tcp"] = tcp_check.success
    if tcp_check.success == True:
        logger.info(f"TCP check passed: {host} {tcp_check.duration:.2f}s")
    else:
        logger.warning(f"TCP check failed: {host} {tcp_check.duration:.2f}s {tcp_check.error}")

        for x in range(retries):
            delay = get_delay(x)
            time.sleep(delay)

            tcp_check = check_tcp_connection(host=host, port=port, timeout=timeout)
            results["tcp"] = tcp_check.success
            if tcp_check.success == True:
                logger.info(f"TCP check passed: {host} {tcp_check.duration:.2f}s after {x+1} retries")
                break
            logger.warning(f"TCP check failed: {host} {tcp_check.duration:.2f}s {tcp_check.error} after {x+1} retries")
    
    http_check = await make_http_request(
        client=client, host=host, healthurl=healthurl
    )
    results["http"] = http_check.success
    if http_check.success == True:
        logger.info(f"HTTP check passed: {host} 200 {http_check.duration:.2f}s")
    else:
        if http_check.details is not None:
            logger.warning(f"HTTP check failed: {host} {http_check.details['status_code']} {http_check.duration:.2f}s")
            if http_check.details['status_code'] >= 500:
                for x in range(retries):
                    delay = get_delay(x)
                    time.sleep(delay)
                    http_check = await make_http_request(
                        client=client, host=host, healthurl=healthurl
                    )
                    results["http"] = http_check.success
                    if http_check.success == True:
                        logger.info(f"HTTP check passed: {host} 200 {http_check.duration:.2f}s after {x+1} retries")
                        break

                    if http_check.details is not None:
                        logger.warning(f"HTTP check failed: {host} {http_check.details['status_code']} {http_check.duration:.2f}s after {x+1} retries")
                    else:
                        logger.warning(f"HTTP check failed: {host} {http_check.duration:.2f}s after {x+1} retries")

    if not all(results.values()):
        raise typer.Exit(code=1)

async def monitor_all(services: list[ServiceConfig]):
    """Creates a shared HTTP clients and spawns all monitoring tasks concurrently"""
    async with httpx.AsyncClient() as client:
        tasks = [healthcheck_orchestrator(
            client, service) for service in services]
        await asyncio.gather(*tasks)

def healthcheck(
    config: Annotated[
        Path, 
        typer.Option(
            "--config", 
            "-c", 
            help="Path to the YAML services configuration file."
        )] = Path("config.yaml")
):
    """Monitor multiple web services concurrently from a configuration file."""
    try:
        if not config.exists():
            raise ConfigError(f"Config file not found: {config}")
    
        services = load_config(config_path=config)
        if not services:
            raise ConfigError("No services in config file")

        logger.info(f"Starting concurrent monitoring for {len(services)} services...")

        asyncio.run(monitor_all(services=services))

    except ConfigError as exc:
        logger.error("Invalid configuration: %s", exc)
        raise typer.Exit(code=1)

    except TypeError as exc:
        logger.error("Invalid type: %s", exc)
        raise typer.Exit(code=1)

    except ValueError as exc:
        logger.error("Unexpected value: %s", exc)
        raise typer.Exit(code=1)
