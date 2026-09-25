import time, requests

from .models import CheckResult

def make_http_request(service: str, healthurl: str):
    """
    Attempts to make an HTTP GET request to a service, 
    measuring the time it takes.
    """
    if not healthurl:
        url = "https://" + service
    else:
        url = healthurl
    
    start_time = time.perf_counter()
    response = requests.get(url)
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
