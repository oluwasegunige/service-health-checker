import typer
from typing_extensions import Annotated

from .dns_check import dns_check
from .check_tcp_connection import check_tcp_connection

def health_check(
    service: Annotated[str, typer.Argument(help="The services to be checked")] = ""
):
    dns_check(service=service)
    print()
    check_tcp_connection(service, 443)
    print()
    