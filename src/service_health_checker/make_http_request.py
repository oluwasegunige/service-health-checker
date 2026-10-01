import time, httpx

from .models import CheckResult
from .is_valid_uri import is_valid_uri

async def make_http_request(
        client: httpx.AsyncClient, host: str, healthurl: str
):
    """
    Attempts to make an HTTP GET request to a service, 
    measuring the time it takes.
    """
    if healthurl == "":
        if host == "":
            raise ValueError("Host/health URL is required for HTTP check.")
        url = "https://" + host
    else:
        url = healthurl

    if not is_valid_uri(url):
        raise ValueError("HealthURL is not a valid URI")
    
    start_time = time.perf_counter()
    response = await client.get(url)
    elapsed_time = (time.perf_counter() - start_time)
    status_code = response.status_code

    if status_code == 200:
        return CheckResult(
            check_type="http",
            success=True,
            duration=elapsed_time
        )
    else:
        return CheckResult(
            check_type="http",
            success=False,
            duration=elapsed_time,
            details={"status_code": status_code}
        )
