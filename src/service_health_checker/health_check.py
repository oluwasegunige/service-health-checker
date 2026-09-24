import typer
from typing_extensions import Annotated

from .dns_check import dns_check

def health_check(
    service: Annotated[str, typer.Argument(help="The services to be checked")] = ""
):
    dns_check(service=service)
    