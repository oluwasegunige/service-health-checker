import yaml

from .logging_config import logger

class ServiceConfig:
    def __init__(self, name, host, port, timeout, healthurl) -> None:
        self.name = name
        self.host = host
        self.port = port
        self.timeout = timeout
        self.healthurl = healthurl

def load_config(config_path):
    tcp_timeout = 3
    tcp_port = 443
    try:
        with open(config_path, "r") as file:
            config_file = yaml.safe_load(file) or {}
            name = config_file.get("name")
            host = config_file.get("host")
            if not host:
                logger.warning("Host is required.")
                exit(1)
            tcp_config = config_file.get("tcp")
            for item in tcp_config or []:
                tcp_timeout = item.get("timeout")
                if item.get("port"):
                    tcp_port = item.get("port")
            healthurl = config_file.get("healthurl")
            if not healthurl:
                healthurl = ""
            service_config = ServiceConfig(
                name=name,
                host=host,
                port=tcp_port,
                timeout=tcp_timeout,
                healthurl=healthurl)
            return service_config
    except FileNotFoundError:
        logger.warning(f"Configuration file {config_path} not found.")
        exit(1)
