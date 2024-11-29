import requests
import json
import logging
from datetime import datetime
from src.assistant.tools.helpers import tool_response, is_valid_config, is_valid_datetime, get_request_session


def get_next_day_5am(current_date):
    try:
        next_day_5am = current_date.replace(day=current_date.day + 1, hour=5, minute=0, second=0, microsecond=0)
        return next_day_5am.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.error(f"Error getting next day 5am: {e}")
        return False

def usage():
    return {
        "type": "function",
        "function": {
            "name": "set_website_availability",
            "description": "This function changes the state of a website to either online or offline, designed for quick adjustments to the website's availability status.",
            "parameters": {
            "type": "object",
            "properties": {
                "is_website_online": {
                "type": "string",
                "enum": ["true", "false"],
                "description": "Sets the website's status. 'true' for online, 'false' for offline."
                },
                "offline_until": {
                "type": "string",
                "format": "date-time",
                "description": "Specifies the datetime until the website remains offline. Defaults to 5am the next day if offline; otherwise, an empty string."
                },
                "offline_message": {
                "type": "string",
                "description": "Custom message displayed when the website is offline. Defaults to a general notice about returning online at 5am the next day."
                }
            },
            "required": ["is_website_online", "offline_until", "offline_message"]
            },
            "context": "Intended for toggling the website's availability. Not for content updates, non-availability messages, or setting holiday closures."
        }
    }


def execute(is_website_online, offline_until, offline_message, config):


    try:
        if not is_valid_config(config, required_config_keys = ["store_id", "authorization_header", "endpoint"]):
            raise ValueError("Invalid 'config' object. Please provide a valid 'store_id', 'authorization_header', and 'endpoint'.")

        # If the offline_until parameter is empty, then set the default value to the next day at 5am
        if not offline_until:
            offline_until = get_next_day_5am(datetime.now())
        
        if not is_valid_datetime(offline_until):
            logging.debug(f"Invalid offline_until: {offline_until}, defaulting to 05:00:00")
            raise ValueError("Invalid 'offline_until' value. Please use a valid date-time format.")    

    
        # Validate the 'online' parameter to ensure it's either "true" or "false"
        if is_website_online not in ["true", "false"]:
            raise ValueError("Invalid 'is_website_online' value. Please use 'true' or 'false'.")

        # Prepare the payload for the PUT request
        payload = f"online={is_website_online}&online_closed_till={offline_until}&online_msg={offline_message}"
        logging.debug(f"Payload for updating website status: {payload}")

        # Specify the API URL
        url = f"{config['endpoint']}/settings/{config['store_id']}"
        logging.warning(f"URL: {url}")
        # Define the headers for the request
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Authorization': config['authorization_header'],
                   'passport': '1'}
        
        # Dropping headers because JWT is short lived and won't live enough for you to use it to complete this test
        headers = {}
        # Bolting a static API TOKEN into the GET params for the sake of this test
        SECRET_API_TOKEN = ""
        url = f"{url}&api_token={SECRET_API_TOKEN}"


        # Get request session
        r = get_request_session()
        # Sending the PUT request to the API
        response = r.put(url, headers=headers, data=payload)

        # Log warning: dump request
        logging.warning(f"API request: {response.request.url}")
        logging.warning(f"API request headers: {response.request.headers}")
        logging.warning(f"API request body: {response.request.body}")

        # Log warning: dump response
        logging.warning(f"API response status code: {response.status_code}")
        logging.warning(f"API response headers: {response.headers}")
        logging.warning(f"API response body: {response.text}")
        

        if response.status_code != 200:
            raise ValueError(f"API error: {response.status_code}")

        # Parse and return the response
        result = response.json()
        
        return json.dumps(result)
    except Exception as e:
        logging.error(f"{usage()['function']['name']} {e}")
        # return f"Error {usage['function']['name']}. Inform the user this is temporarily unavailable"
        return json.dumps({"status": "failed"})
    