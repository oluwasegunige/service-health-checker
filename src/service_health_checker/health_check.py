import typer
from typing_extensions import Annotated

from .logging_config import logger
from .dns_check import check_dns
from .check_tcp_connection import check_tcp_connection
from .make_http_request import make_http_request

def health_check(
    service: Annotated[str, typer.Argument(help="The services to be checked")] = ""
):
    check_dns(service=service)
    check_tcp_connection(host=service, port=443)
    make_http_request(service=service)
    