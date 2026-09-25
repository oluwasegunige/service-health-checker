import typer
from typing_extensions import Annotated

from .logging_config import logger
from .dns_check import check_dns
from .check_tcp_connection import check_tcp_connection
from .make_http_request import make_http_request

def healthcheck(
    service: Annotated[str, typer.Argument(help="The services to be checked")] = "",
    port: Annotated[int, typer.Option(help="The port on which to attempt TCP connection")] = 443,
    timeout: Annotated[float, typer.Option(help="The timeout duration for the TCP check")] = 3.0,
    healthurl: Annotated[str, typer.Option(help="The complete HTTP health check url")] = ""
):
    results = {}

    dns_check = check_dns(service=service)
    results["dns"] = dns_check.success
    if dns_check.success == True:
        if dns_check.details is not None:
            logger.info(f"DNS check passed: {service} {dns_check.details["ip_address"]} {dns_check.duration:.2f}s")
        else:
            logger.info(f"DNS check passed: {service} {dns_check.duration:.2f}s")
    else:
        logger.error(f"DNS check failed: {service} {dns_check.duration:.2f}s {dns_check.error}")

    tcp_check = check_tcp_connection(host=service, port=port, timeout=timeout)
    results["tcp"] = tcp_check.success
    if tcp_check.success == True:
        logger.info(f"TCP check passed: {service} {tcp_check.duration:.2f}s")
    else:
        logger.error(f"TCP check failed: {service} {tcp_check.duration:.2f}s {tcp_check.error}")
    
    http_check = make_http_request(service=service, healthurl=healthurl)
    results["http"] = http_check.success
    if http_check.success == True:
        logger.info(f"HTTP check passed: {service} 200 {http_check.duration:.2f}s")
    else:
        if http_check.details is not None:
            logger.error(f"HTTP check failed: {service} {http_check.details['status_code']} {http_check.duration:.2f}s")
        else:
            logger.error(f"HTTP check failed: {service} {http_check.duration:.2f}s")

    for v in results.values():
        if v == False:
            exit(1)
    exit(0)
