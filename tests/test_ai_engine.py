import pytest
from unittest.mock import patch, MagicMock
from modules.ai_engine import extract_iocs_ttps_gpt, summarize_threat_report

class MockUsage:
    def __init__(self):
        self.total_tokens = 100

class MockResponse:
    def __init__(self, content):
        self.content = content
        self.model = "gpt-4"
        self.usage = MockUsage()

@patch('modules.ai_engine.get_provider')
def test_extract_iocs_ttps_gpt(mock_get_provider):
    mock_provider = MagicMock()
    # Mocking the AI response to be valid JSON
    mock_provider.generate.return_value = MockResponse('{"indicators_of_compromise": {"ips": ["1.1.1.1"]}, "ttps": [{"mitre_id": "T1548"}]}')
    mock_get_provider.return_value = mock_provider
    
    result = extract_iocs_ttps_gpt(
        text="Sample text",
        openai_api_key="fake_key",
        provider_name="openai",
        model_name="gpt-4"
    )
    
    # We should get back the exact JSON string since OutputValidator handles parsing later in the pipeline
    assert "1.1.1.1" in result
    assert "T1548" in result

@patch('modules.ai_engine.get_provider')
def test_summarize_threat_report(mock_get_provider):
    mock_provider = MagicMock()
    mock_provider.generate.return_value = MockResponse("This is a summary.")
    mock_get_provider.return_value = mock_provider
    
    result = summarize_threat_report(
        text="Sample text",
        openai_api_key="fake_key",
        provider_name="openai",
        model_name="gpt-4"
    )
    
    assert result == "This is a summary."
