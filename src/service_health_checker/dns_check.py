import time, socket

def dns_check(service):
    try:
        start_time = time.perf_counter()
        ip_address = socket.gethostbyname(service)
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        print(f"Service: {service}")
        print(f"IP Address: {ip_address}")
        print(f"Lookup Time: {duration_ms:.2f} ms")
    except socket.gaierror as e:
        print(f"DNS lookup failed for {service}: {e}")
        