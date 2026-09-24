import typer, logging
from typing_extensions import Annotated

from .logging_config import logger
from .dns_check import dns_check
from .check_tcp_connection import check_tcp_connection
from .make_http_request import make_http_request

def health_check(
    service: Annotated[str, typer.Argument(help="The services to be checked")] = ""
):
    dns_check_result = dns_check(service=service)
    if dns_check_result["success"] == True:
        ip_address = dns_check_result["ip_address"]
        duration = dns_check_result["duration"]
        logger.info(f"DNS check passed: {service} {ip_address} {duration:.2f}s")
    else:
        error = dns_check_result["error"]
        logger.error(f"DNS check failed: {service} {error}")

    tcp_check_result = check_tcp_connection(host=service, port=443)
    if tcp_check_result["success"] == True:
        duration = tcp_check_result["duration"]
        logger.info(f"TCP check passed: {service} {duration:.2f}s")
    else:
        message = tcp_check_result["message"]
        logger.error(f"TCP check failed: {service} {message}")

    http_check_result = make_http_request(service=service)
    status_code = http_check_result["status_code"]
    duration = http_check_result["duration"]
    if status_code == 200:
        logger.info(f"HTTP check passed: {service} {status_code} {duration:.2f}s")
    elif status_code < 500:
        logger.warning(f"Unexpected HTTP result: {service} {status_code} {duration:.2f}s")
    else:
        logger.error(f"HTTP check failed: {service} {status_code} {duration:.2f}s")
    