import time, requests

def make_http_request(service: str):
    """
    Attempts to make an HTTP GET request to a service, 
    measuring the time it takes.
    """
    url = "https://" + service
    
    start_time = time.perf_counter()
    response = requests.get(url)
    elapsed_time = (time.perf_counter() - start_time)

    return {
        "success": True,
        "status_code": response.status_code,
        "duration": elapsed_time
    }
