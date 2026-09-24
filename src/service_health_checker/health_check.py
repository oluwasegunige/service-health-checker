import typer, logging
from typing_extensions import Annotated

from .dns_check import dns_check
from .check_tcp_connection import check_tcp_connection

def health_check(
    service: Annotated[str, typer.Argument(help="The services to be checked")] = ""
):
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')

    dns_check_result = dns_check(service=service)
    if dns_check_result["success"] == True:
        ip_address = dns_check_result["ip_address"]
        duration = dns_check_result["duration"]
        logging.info(f"DNS check passed: {service} {ip_address} {duration:.2f}s")
    else:
        error = dns_check_result["error"]
        logging.error(f"DNS check failed: {service} {error}")
    print()
    check_tcp_connection(service, 443)
    print()
    