import pytest
import pandas as pd
import sys
import os
from os.path import dirname, abspath
from datetime import datetime
from typing import List

from src.assistant.tools.set_website_availability.set_website_availability import get_next_day_5am, execute, get_request_session


from unittest.mock import patch

def test_get_next_day_5am_with_valid_date():
    current_date = datetime.now()
    next_day_5am = current_date.replace(day=current_date.day + 1, hour=5, minute=0, second=0, microsecond=0)
    assert get_next_day_5am(current_date) == next_day_5am.strftime("%Y-%m-%d %H:%M:%S")

def test_get_next_day_5am_with_invalid_date():
    current_date = "invalid"
    assert get_next_day_5am(current_date) == False


# @patch('src.assistant.tools.set_website_availability.set_website_availability.execute.response')
# def test_set_website_availability_online(mock_execute):
#     # Test case 1
#     params = {
#         "is_website_online": "true",
#         "offline_until": "2022-01-01T05:00:00",
#         "offline_message": "We are currently offline. We will be back online at 5am.",
#         "config" : {
#             "store_id": "123",
#             "authorization_header" : "Bearer 123"
#         }
#     }
#     mock_execute.return_value = {"status": "succeeded"}
#     result = execute(**params)
#     assert result == {"status": "succeeded"}



# def test_set_website_availability_offline():
#     # Test case 2
#     params = {
#         "is_website_online": "false",
#         "offline_until": "2022-01-01T05:00:00",
#         "offline_message": "We are currently offline. We will be back online at 5am.",
#         "config" : {
#             "store_id": "123",
#             "authorization_header" : "Bearer 123"
#         }
#     }
#     result = execute(**params)
#     assert result == {"status": "succeeded"}

# def test_set_website_availability_invalid_offline_until():
#     # Test case 3
#     params = {
#         "is_website_online": "false",
#         "offline_until": "2022-01-01T05:00:00",
#         "offline_message": "We are currently offline. We will be back online at 5am.",
#         "config" : {
#             "store_id": "123",
#             "authorization_header" : "Bearer 123"
#         }
#     }
#     result = execute(**params)
#     assert result == {"status": "failed"}

# def test_set_website_availability_invalid_is_website_online():
#     # Test case 4
#     params = {
#         "is_website_online": "invalid",
#         "offline_until": "2022-01-01T05:00:00",
#         "offline_message": "We are currently offline. We will be back online at 5am.",
#         "config" : {
#             "store_id": "123",
#             "authorization_header" : "Bearer 123"
#         }
#     }
#     result = execute(**params)
#     assert result == {"status": "failed"}



# # Read the test data
# test_data = pd.read_csv("./set_website_availability_prompts.csv")



# def test_set_website_availability_prompts():
#     for test_idx, test_case in test_data.iterrows():
#         # Execute the function
#         result = execute(
#             test_case["is_website_online"],
#             test_case["offline_until"],
#             test_case["offline_message"],
#             test_case["store_id"],
#             test_case["authorization_header"]
#         )
#         # Check the result
#         assert result == test_case["expected_result"]

