import pytest
from modules.pipeline.output_validator import OutputValidator

def test_validate_json_valid():
    valid_json = '{"sigma_title": "Test Title", "indicators_of_compromise": {}}'
    is_valid, data = OutputValidator.validate_json(valid_json)
    assert is_valid is True
    assert data["sigma_title"] == "Test Title"

def test_validate_json_with_markdown_blocks():
    markdown_json = "```json\n{\"key\": \"value\"}\n```"
    is_valid, data = OutputValidator.validate_json(markdown_json)
    assert is_valid is True
    assert data["key"] == "value"

def test_repair_json_invalid_escapes():
    invalid_json = '{"path": "C:\\\\Windows\\\\System32"}'
    is_valid, data = OutputValidator.validate_json(invalid_json)
    assert is_valid is True
    assert "C:\\Windows\\System32" in data["path"] or "C:\\\\Windows\\\\System32" in data["path"]

def test_repair_json_trailing_comma():
    trailing_comma_json = '{"a": 1, "b": 2,}'
    is_valid, data = OutputValidator.validate_json(trailing_comma_json)
    assert is_valid is True
    assert data["b"] == 2

def test_repair_json_truncated():
    truncated_json = '{"a": 1, "b": {"c": 2'
    is_valid, data = OutputValidator.validate_json(truncated_json)
    assert is_valid is True
    assert data["a"] == 1
    assert data["b"]["c"] == 2

def test_validate_ioc_response_missing_fields():
    data = {}
    is_valid, new_data, warnings = OutputValidator.validate_ioc_response(data)
    assert is_valid is False
    assert len(warnings) > 0
    assert "sigma_title" in new_data
    assert "indicators_of_compromise" in new_data
    assert "ips" in new_data["indicators_of_compromise"]

def test_validate_siem_response_missing_platform():
    data = {"splunk": {"description": "D", "query": "Q", "notes": "N"}}
    is_valid, new_data, warnings = OutputValidator.validate_siem_response(data)
    assert is_valid is False
    assert "qradar" in new_data
    assert new_data["qradar"]["query"].startswith("ERROR")

def test_validate_sigma_yaml_valid():
    yaml_str = "title: Test\nlogsource: windows\ndetection: test\nlevel: high\n"
    is_valid, warnings = OutputValidator.validate_sigma_yaml(yaml_str)
    assert is_valid is True
    assert len(warnings) == 0

def test_validate_sigma_yaml_invalid_level():
    yaml_str = "title: Test\nlogsource: windows\ndetection: test\nlevel: invalid\n"
    is_valid, warnings = OutputValidator.validate_sigma_yaml(yaml_str)
    assert is_valid is False
    assert any("Invalid level" in w for w in warnings)
