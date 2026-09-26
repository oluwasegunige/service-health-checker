import pytest, sys

import yaml

from src.service_health_checker.config import load_config, ServiceConfig
from src.service_health_checker.logging_config import logging

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


def test_load_config_with_host_omitted(caplog):
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

    with pytest.raises(SystemExit) as failed_load:
        load_config(yaml_file)
    assert failed_load.value.code == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert "Host is required." in caplog.text


def test_load_config_with_host_empty(caplog):
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

    with pytest.raises(SystemExit) as failed_load:
        load_config(yaml_file)
    assert failed_load.value.code == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert "Host is required." in caplog.text


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


def test_load_config_with_file_not_exists(caplog):
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
    
    with pytest.raises(SystemExit) as failed_load:
        load_config(wrong_file)
    assert failed_load.value.code == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert f"Configuration file {wrong_file} not found." in caplog.text


def test_load_config_with_empty_file(caplog):
    yaml_file = "tests/test_config.yaml"

    yaml_content = {}

    with open(yaml_file, "w") as file:
        yaml.dump(
            yaml_content, file, default_flow_style=False, sort_keys=False)
    
    with pytest.raises(SystemExit) as failed_load:
        load_config(yaml_file)
    assert failed_load.value.code == 1
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    assert "Host is required." in caplog.text

