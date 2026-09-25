import time, socket

from .models import CheckResult

def check_tcp_connection(host: str, port: int, timeout: float):
    """
    Attempts to establish a TCP connection to a host and port, 
    measuring the time it takes.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    start_time = time.perf_counter()

    try:
        sock.connect((host, port))
        elapsed_time = (time.perf_counter() - start_time)
        return CheckResult(
            check_type="tcp",
            success=True,
            duration=elapsed_time
        )
    except socket.timeout:
        return CheckResult(
            check_type="tcp",
            success=False,
            duration=timeout,
            error=f"Socket timeout after {timeout}s"
        )
    except socket.error as e:
        elapsed_time = (time.perf_counter() - start_time)
        print(e)
        return CheckResult(
            check_type="tcp",
            success=False,
            duration=elapsed_time,
            error=f"Socket error: {str(e)}"
        )
    finally:
        sock.close()
