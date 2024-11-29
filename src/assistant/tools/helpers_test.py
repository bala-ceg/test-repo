from datetime import datetime
from src.assistant.tools.helpers import tool_response, is_valid_config, is_valid_datetime

def test_is_valid_config_with_valid_config():
    config = {
        "store_id": "123",
        "authorization": "Bearer 123",
        "endpoint": "https://example.com"
    }
    required_config_keys = ["store_id", "authorization", "endpoint"]
    assert is_valid_config(config, required_config_keys) == True

def test_is_valid_config_with_empty_keys():
    config = {
        "store_id": "",
        "authorization": "",
        "endpoint": ""
    }
    required_config_keys = ["store_id", "authorization", "endpoint"]
    assert is_valid_config(config, required_config_keys) == False

def test_is_valid_config_with_missing_keys():
    config = {
        "store_id": "123",
        "endpoint": "https://example.com"
    }
    required_config_keys = ["store_id", "authorization", "endpoint"]
    assert is_valid_config(config, required_config_keys) == False


def test_is_valid_datetime_with_future_date():
    future_date = datetime.now().replace(year=datetime.now().year + 1).strftime("%Y-%m-%d %H:%M:%S")
    assert is_valid_datetime(future_date) == True

def test_is_valid_datetime_with_incomplete_date():
    incomplete_date = datetime.now().replace(year=datetime.now().year + 1).strftime("%Y-%m-%d")
    assert is_valid_datetime(incomplete_date) == False

def test_is_valid_datetime_with_past_date():
    a_year_ago = datetime.now().replace(year=datetime.now().year - 1).strftime("%Y-%m-%d %H:%M:%S")
    assert is_valid_datetime(a_year_ago) == False

def test_is_valid_datetime_with_invalid_date():
    invalid_date = "invalid"
    assert is_valid_datetime(invalid_date) == False
