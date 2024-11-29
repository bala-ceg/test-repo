# from dotenv import load_dotenv
import os
from dotenv import load_dotenv
# Load the .env file
load_dotenv()

# Constants for easier configuration and maintenance
OPENAI_API_KEY = os.environ.get('ASSISTANT_OPENAI_API_KEY')
OPENAI_BASE_URL = os.environ.get('ASSISTANT_OPENAI_BASE_URL')
GPT_MODEL = os.environ.get('ASSISTANT_GPT_MODEL')
GPT3_MODEL = os.environ.get('ASSISTANT_GPT_MODEL')
GPT4_MODEL = os.environ.get('ASSISTANT_GPT_MODEL')

# Redis configuration using environment variables
REDIS_CONFIG = {
    'host': os.getenv('ASSISTANT_REDIS_HOST', 'redis'),
    'port': int(os.getenv('ASSISTANT_REDIS_PORT', 6379)),
    'db': int(os.getenv('ASSISTANT_REDIS_DB', 0)),
    'decode_responses': True  # Decode responses from bytes to str
}

# Endpoint
BASE_URL = os.environ.get('TOOLS_BASE_URL')