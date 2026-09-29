import pytest, yaml

from src.service_health_checker.config import load_config, ServiceConfig, ConfigError

def test_load_config_with_all_values():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "example.com",
        "tcp": [
            {"port": 443},
            {"timeout": 3}
        ],
        "healthurl": "https://example.com/v1/health",
        "retries": 2
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert isinstance(result, ServiceConfig)


def test_load_config_with_only_required_values():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "host": "example.com",
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert isinstance(result, ServiceConfig)
    assert result.port == 443
    assert result.timeout == 3
    assert result.healthurl == ""
    assert result.retries == 2


def test_load_config_with_tcp_timeout_supplied():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "host": "example.com",
        "tcp": [
            {"timeout": 5}
        ],
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert result.timeout == 5


def test_load_config_with_tcp_port_supplied():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "host": "example.com",
        "tcp": [
            {"port": 80},
        ],
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert result.port == 80


def test_load_config_with_healthurl_supplied():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "host": "example.com",
        "healthurl": "https://example.com/v1/health",
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert result.healthurl == "https://example.com/v1/health"


def test_load_config_with_retries_supplied():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "host": "example.com",
        "retries": 3
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert result.retries == 3


def test_load_config_with_healthurl_omitted():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "example.com",
        "tcp": [
            {"port": 80},
            {"timeout": 3}
        ],
        "retries": 2
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert result.healthurl == ""


def test_load_config_with_retries_omitted():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "example.com",
        "tcp": [
            {"port": 80},
            {"timeout": 3}
        ],
        "healthurl": "https://example.com/v1/health"
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert result.retries == 2


def test_load_config_with_host_omitted():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "tcp": [
            {"port": 443},
            {"timeout": 3}
        ],
        "healthurl": "https://example.com/v1/health",
        "retries": 2
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    with pytest.raises(ConfigError) as failed_load:
        load_config(yaml_file)

    assert str(failed_load.value) == "Host not provided"


def test_load_config_with_host_empty():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "",
        "tcp": [
            {"port": 443},
            {"timeout": 3}
        ],
        "healthurl": "https://example.com/v1/health",
        "retries": 2
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    with pytest.raises(ConfigError) as failed_load:
        load_config(yaml_file)

    assert str(failed_load.value) == "Host not provided"


def test_load_config_with_no_tcp():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "example.com",
        "healthurl": "https://example.com/v1/health",
        "retries": 2
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    result = load_config(yaml_file)
    assert result.timeout == 3
    assert result.port == 443

def test_load_config_with_tcp_port_str():
    tcp_port = "banana"
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "example.com",
        "tcp": [
            {"port": tcp_port},
            {"timeout": 3}
        ],
        "healthurl": "https://example.com/v1/health",
        "retries": 2
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)
    
    with pytest.raises(
        ConfigError, 
        match=f"Expected an int as port, but got {type(tcp_port).__name__}"
    ) as load_config_with_tcp_port_str:
        load_config(yaml_file)
    assert str(load_config_with_tcp_port_str.value) == f"Expected an int as port, but got {type(tcp_port).__name__}"


def test_load_config_with_retries_str():
    retries = "banana"
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "example.com",
        "tcp": [
            {"port": 443},
            {"timeout": 3}
        ],
        "healthurl": "https://example.com/v1/health",
        "retries": retries
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)
    
    with pytest.raises(
        ConfigError, 
        match=f"Expected retries as int, but got {type(retries).__name__}"
    ) as load_config_with_retries_str:
        load_config(yaml_file)
    assert str(load_config_with_retries_str.value) == f"Expected retries as int, but got {type(retries).__name__}"


def test_load_config_with_file_not_exists():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {
        "name": "example",
        "host": "example.com",
        "tcp": [
            {"port": 443},
            {"timeout": 3}
        ],
        "healthurl": "https://example.com/v1/health",
        "retries": 2
    }

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    wrong_file = "tests/nofile.yaml"
    
    with pytest.raises(ConfigError) as failed_load:
        load_config(wrong_file)

    assert str(failed_load.value) == f"Configuration file {wrong_file} not found."


def test_load_config_with_empty_file():
    yaml_file = "tests/test_config.yaml"

    yaml_content = {}

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)

    with pytest.raises(ConfigError) as failed_load:
        load_config(yaml_file)

    assert str(failed_load.value) == "Host not provided"

