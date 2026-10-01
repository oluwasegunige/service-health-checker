import yaml

class ServiceConfig:
    def __init__(self, host, port, timeout, healthurl, retries) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.healthurl = healthurl
        self.retries = retries

class ConfigError(Exception):
    pass

def get_service_details(service: dict) -> ServiceConfig:
    tcp_timeout = 3
    tcp_port = 443

    host = service.get("host", "")
    if not host:
        raise ConfigError("Host not provided")

    tcp_config = service.get("tcp", [])
    for item in tcp_config:
        if "timeout" in item:
            tcp_timeout = item.get("timeout")
            if not isinstance(tcp_timeout, float) and not isinstance(tcp_timeout, int):
                raise ConfigError(f"Expected a number as timeout, but got {type(tcp_timeout).__name__}")
            if tcp_timeout < 1:
                raise ConfigError("Timeout must be a positive number")
        if "port" in item:
            tcp_port = item.get("port")
            if not isinstance(tcp_port, int):
                raise ConfigError(f"Expected an int as port, but got {type(tcp_port).__name__}")
            if tcp_port < 1 or tcp_port > 65535:
                raise ConfigError("Port must be an integer in the valid TCP port range (1–65535)")
            
    healthurl = service.get("healthurl")
    if not healthurl:
        healthurl = ""

    retries = service.get("retries")
    if retries and not isinstance(retries, int):
        raise ConfigError(f"Expected retries as int, but got {type(retries).__name__}")

    if retries and retries < 0:
        raise ConfigError("Retries must be a positive number")
    
    if not retries:
        retries = 2

    service_config = ServiceConfig(
        host=host,
        port=tcp_port,
        timeout=tcp_timeout,
        healthurl=healthurl,
        retries=retries)
    return service_config

def load_config(config_path) -> list[ServiceConfig]:
    try:
        with open(config_path, "r") as file:
            config_file = yaml.safe_load(file) or {}

            services = []
            services_config = config_file.get("services", [])

            if not services_config:
                raise ConfigError("No services found in config file")

            for service in services_config:
                services.append(get_service_details(service))
                
            return services
    except FileNotFoundError:
        raise ConfigError(f"Configuration file {config_path} not found.")
    except yaml.YAMLError as exc:
        raise ConfigError(f"Error parsing YAML file: {exc}")
