import time, socket

def dns_check(service):
    """
    Attempts to perform a forward DNS lookup to a service, 
    measuring the time it takes.
    """
    try:
        start_time = time.perf_counter()
        ip_address = socket.gethostbyname(service)
        end_time = time.perf_counter()
        duration = (end_time - start_time)
        return {
            "success": True,
            "ip_address": ip_address,
            "duration": duration
        }
    except socket.gaierror as e:
        return {
            "success": False,
            "error": e
        }
