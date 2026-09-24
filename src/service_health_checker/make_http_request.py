import time, requests

def make_http_request(service: str):
    """
    Attempts to make an HTTP GET request to a service, 
    measuring the time it takes.
    """
    print("---MAKE HTTP REQUEST---")
    url = "https://" + service
    
    start_time = time.perf_counter()
    response = requests.get(url)
    elapsed_time = (time.perf_counter() - start_time)

    if response.status_code == 200:
        print(f"HTTP GET request to {url} successful after {elapsed_time:.2f} seconds.")
    else:
        print(
            f"HTTP GET request to {url} returned {response.status_code} after {elapsed_time:.2f} seconds.")
