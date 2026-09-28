import yaml

class ServiceConfig:
    def __init__(self, name, host, port, timeout, healthurl, retries) -> None:
        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout
        self.healthurl = healthurl
        self.retries = retries

class ConfigError(Exception):
    pass

def load_config(config_path):
    tcp_timeout = 3
    tcp_port = 443
    try:
        with open(config_path, "r") as file:
            config_file = yaml.safe_load(file) or {}

            name = config_file.get("name")

            host = config_file.get("host")
            if not host:
                raise ConfigError("Host not provided")

            tcp_config = config_file.get("tcp")
            for item in tcp_config or []:
                if "timeout" in item:
                    tcp_timeout = item.get("timeout")
                if "port" in item:
                    tcp_port = item.get("port")
                    if not isinstance(tcp_port, int):
                        raise ConfigError(f"Expected an int, but got {type(tcp_port).__name__}")
                    
            healthurl = config_file.get("healthurl")
            if not healthurl:
                healthurl = ""

            retries = config_file.get("retries")
            if not retries:
                retries = 2

            service_config = ServiceConfig(
                name=name,
                host=host,
                port=tcp_port,
                timeout=tcp_timeout,
                healthurl=healthurl,
                retries=retries)
            return service_config
    except FileNotFoundError:
        raise ConfigError(f"Configuration file {config_path} not found.")
