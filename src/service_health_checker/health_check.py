import typer
from typing_extensions import Annotated

from .logging_config import logger
from .dns_check import check_dns
from .check_tcp_connection import check_tcp_connection
from .make_http_request import make_http_request

def health_check(
    service: Annotated[str, typer.Argument(help="The services to be checked")] = ""
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

    tcp_check = check_tcp_connection(host=service, port=443)
    results["tcp"] = tcp_check.success
    if tcp_check.success == True:
        logger.info(f"TCP check passed: {service} {tcp_check.duration:.2f}s")
    else:
        logger.error(f"TCP check failed: {service} {tcp_check.duration:.2f}s {tcp_check.error}")
    
    http_check = make_http_request(service=service)
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
