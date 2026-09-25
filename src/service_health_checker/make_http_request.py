import time, requests

from .models import CheckResult

def make_http_request(service: str):
    """
    Attempts to make an HTTP GET request to a service, 
    measuring the time it takes.
    """
    url = "https://" + service
    
    start_time = time.perf_counter()
    response = requests.get(url)
    elapsed_time = (time.perf_counter() - start_time)
    status_code = response.status_code

    if status_code == 200:
        CheckResult(
            service=service,
            check_type="http",
            success=True,
            duration=elapsed_time
        )
    else:
        CheckResult(
            service=service,
            check_type="http",
            success=False,
            duration=elapsed_time,
            details={"status_code": status_code}
        )
