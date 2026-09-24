import time, socket

def check_tcp_connection(host: str, port: int, timeout: float = 3.0):
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
        return {
            "success": True, 
            "duration": elapsed_time
        }
    except socket.timeout:
        return {
            "success": False, 
            "message": f"Socket timeout after {timeout}s"
        }
    except socket.error as e:
        return {
            "success": False,
            "message": f"Socket error: {e}"
        }
    finally:
        sock.close()
