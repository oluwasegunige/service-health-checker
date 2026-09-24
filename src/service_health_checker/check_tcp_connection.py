import time, socket

def check_tcp_connection(host: str, port: int, timeout: float = 3.0):
    """
    Attempts to establish a TCP connection to a host and port, 
    measuring the time it takes.
    """
    print("---CHECK TCP CONNECTION---")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    start_time = time.perf_counter()

    try:
        sock.connect((host, port))
        elapsed_time = (time.perf_counter() - start_time) * 1000
        print(f"Connected to {host}:{port} in {elapsed_time:.2f} ms")
        return True, elapsed_time
    except socket.timeout:
        print(f"Connection to {host}:{port} timed out after {timeout} seconds.")
        return False, None
    except socket.error as e:
        print(f"Connection to {host}:{port} failed: {e}")
        return False, None
    finally:
        sock.close()