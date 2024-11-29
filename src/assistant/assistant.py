import os
import sys
import importlib
import json
import logging
from openai import OpenAI
from .instructions import process_request_system_instructions, screen_request_system_instructions,process_request_files_instructions

from src import config
from src.assistant.tools.helpers import bootstrap_tools, valid_toolset

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s\n')

# Initialize the OpenAI client
client = OpenAI(api_key=config.OPENAI_API_KEY,base_url=config.OPENAI_BASE_URL)

# Load the tools
current_file_directory = os.path.dirname(os.path.abspath(__file__))
tools_path = os.path.join(current_file_directory, 'tools')
sys.path.append(tools_path)
toolset = bootstrap_tools(tools_path)



class NoRequestError(ValueError):
    """Raised when no request is provided to screen."""
class NoToolsAvailableError(ValueError):
    """Raised when no tools are provided for the screening request."""
class ModelResponseError(Exception):
    """Raised when there's an issue retrieving the response from the model."""
class ResponseParsingError(ValueError):
    """Raised when the response from the model cannot be parsed correctly."""

def screen_request(request, toolset):

    if not request:
        raise NoRequestError("No request provided to screen")

    if not toolset:
        raise NoToolsAvailableError("No tools available to screen request")

    #logging.info(f"request,tool: {request}, {toolset}")
    # Attempt to get a response from the model
    try:
        resp = get_model_response(screen_request_system_instructions(), request, toolset)
        raw_resp = resp.choices[0].message.content
    except Exception as e:
        logging.error(f"Failed to get response from model: {e}")
        raise ModelResponseError("Failed to get response from model") from e
    
    # Attempt to parse and clean the response
    try:
        logging.warning("Raw response: %s", raw_resp)
        filtered_resp = clean_response(raw_resp)
        filtered_resp = json.loads(filtered_resp)
        logging.warning("Filtered response: %s", filtered_resp)
        logging.warning("Request breakdown: %s", filtered_resp["request_breakdown"]["category"])
        return {
            "request_category": filtered_resp["request_breakdown"]["category"],
            "recommended_tool": filtered_resp["exact_tool_name"],
            "recommended_tool_params": filtered_resp["exact_tool_params"],
        }
    except Exception as e:
        logging.error(f"Error processing model response: {e}")
        raise ResponseParsingError("Error processing model response") from e

def get_model_response(system_instructions, request, toolset):

    if not system_instructions:
        raise ValueError("No system instructions provided to get model response")
    
    if not request:
        raise ValueError("No request provided to get model response")
    
    valid_toolset(toolset)
    

    return client.chat.completions.create(
        model=config.GPT_MODEL,
        messages=[
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": f"```request: {request}```"}
        ],
        temperature=0.2,
        tools=toolset.get('definitions'),
    )

def clean_response(raw_resp):
    try:
        # Extract and clean JSON string from raw response
        filtered_resp = raw_resp.split('```json')[1].split('```')[0]
        filtered_resp = filtered_resp.encode('ascii', 'ignore').decode('ascii')
        filtered_resp = filtered_resp.replace("functions.", "")
        return filtered_resp
    except IndexError as e:
        raise ResponseParsingError("Failed to extract JSON from response") from e


class UnsupportedCategoryError(Exception):
    def __init__(self, category, message="The request category is not supported."):
        self.category = category
        self.message = f"{message} Category: '{category}'"
        super().__init__(self.message)

class ToolNotFoundError(Exception):
    def __init__(self, tool_name, message="The recommended tool does not exist."):
        self.tool_name = tool_name
        self.message = f"{message} Tool: '{tool_name}'"
        super().__init__(self.message)

class CommandLoadingError(Exception):
    def __init__(self, tool_name, error, message="An error occurred while evaluating the screen result."):
        self.tool_name = tool_name
        self.error = error
        self.message = f"{message} Error: {error}"
        super().__init__(self.message)

class ScreenRespMissingKeys(Exception):
    def __init__(self, missing_key, message="An error occurred while parsing the screen result."):
        self.missing_key = missing_key
        self.message = f"{message} Missing key: '{missing_key}'"
        super().__init__(self.message)

def evaluate_screen_request(toolset: dict, screen_resp: dict, supported_categories: list):

    valid_toolset(toolset)

    try:
        category = screen_resp['request_category']
        tool_name = screen_resp['recommended_tool']
    except KeyError as e:
        raise ScreenRespMissingKeys(missing_key=e)

    # Validate the request category 
    if category not in supported_categories:
        raise UnsupportedCategoryError(category)

    # Validate a tool has been recommended, and was not hallucinated
    if tool_name == "" or tool_name not in toolset.get('tools'):
        raise ToolNotFoundError(tool_name)

    try:
        # Import the tool module and get the usage
        command = sys.modules[f"{tool_name}.{tool_name}"]
        tool_definition = [command.usage()]
        return tool_definition, tool_name
    except Exception as e:
        raise CommandLoadingError(tool_name, error=e)


def process_request(system_instructions=None, request=None, toolset=None, tool_config=None):

    logging.info("Processing request")
    logging.info("System Instructions: %s", system_instructions)
    logging.info("Request: %s", request)
    logging.info("Toolset: %s", toolset)
    logging.info("Tool Config: %s", tool_config)


   
    try:
        if not system_instructions and 'tools' in toolset and toolset['tools'][0] == 'list_files':
            system_instructions = process_request_files_instructions()
        else:
            system_instructions = process_request_system_instructions()
    except KeyError as e:
        logging.error("KeyError: Missing expected key in tool_config: %s", e)

    except IndexError as e:
        logging.error("IndexError: 'tools' list in tool_config might be empty: %s", e)
    
    if not request:
        raise NoRequestError("No request provided to process")

    if not toolset:
        raise NoToolsAvailableError("No tools available to process request")
    
   
    assistant_conversation = [
        {"role" : "system", "content": system_instructions},
        {"role" : "user", "content" : request}
    ]

    logging.log(logging.INFO, "Assistant conversation: %s", assistant_conversation)
   
    resp = client.chat.completions.create(
        model=config.GPT_MODEL,
        messages=assistant_conversation,
        tools=toolset.get('definitions'),
        tool_choice="auto",
        temperature=0.0
    )

    response = resp.choices[0].message

    logging.info("Assistants initial response: %s", response)

    invoked_tools = []
    invoked_tool = None
    invoked_tools_resp = []
    if response.tool_calls:
        assistant_conversation.append(response) 

        for tool_call in response.tool_calls:
            if tool_call.function.name not in toolset.get('tools'):
                logging.log(logging.FATAL, "Tool not found: %s", tool_call.function.name)
                continue

            invoked_tool = tool_call.function.name
            logging.info("-----------------------------------------")
            logging.log(logging.INFO, "Function Name: %s", tool_call.function.name)
            logging.log(logging.INFO, "Function Args: %s", json.loads(tool_call.function.arguments))
            
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            logging.log(logging.INFO, "Function Args: %s", function_args)

            # Add the store_id and authorization_header to the function arguments
            if tool_config:
                function_args['config'] = tool_config

            logging.log(logging.INFO, "Tool Config: %s",tool_config)

            command = sys.modules[f"{function_name}.{function_name}"]

            logging.log(logging.INFO, "command: %s", command)

            function_response = command.execute(**function_args)

            logging.log(logging.INFO, "Function Response: %s", json.dumps(function_response))

            logging.log(logging.INFO, "Tool Config: %s",tool_config)

            logging.info("-----------------------------------------")

            assistant_conversation.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response),
            })

        logging.log(logging.INFO, "assistant_conversation: %s",assistant_conversation)  
        
        # Process the tool call response
        resp = client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=assistant_conversation,
        )

        logging.log(logging.INFO, "resp: %s",resp)  

        # Add the response to the conversation
        response = resp.choices[0].message
        # assistant_conversation.append(response)

        logging.info("Agent: %s", response.content)
        return response.content, invoked_tool
    else:
        # Not a tool call, continue as normal
        logging.log(logging.FATAL, "No tool calls found in request, we should never get here")
        return response.content
        # pass
        # assistant_conversation.append(response)

