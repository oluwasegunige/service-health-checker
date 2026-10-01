import time, socket

from .models import CheckResult

async def check_dns(host:str):
    """
    Attempts to perform a forward DNS lookup to a service, 
    measuring the time it takes.
    """
    if host == "":
        raise ValueError("Hostname is required")
        
    start_time = time.perf_counter()
    try:
        ip_address = socket.gethostbyname(host)
        end_time = time.perf_counter()
        duration = (end_time - start_time)
        return CheckResult( 
            check_type="dns", 
            success=True, 
            duration=duration,
            details={"ip_address": ip_address})
        
    except socket.gaierror as e:
        duration = time.perf_counter() - start_time
        return CheckResult(
            check_type="dns",
            success=False,
            duration=duration,
            error=str(e)
        )
