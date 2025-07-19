import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Load YAML configuration
config_path = Path(__file__).parent / 'config.yaml'
with open(config_path, 'r') as f:
    config = yaml.safe_load(f)

# AI Configuration
AI_PROVIDER = config['ai']['provider']
AI_MODEL = config['ai']['model']
AI_TEMPERATURE = config['ai']['temperature']
AI_MAX_TOKENS = config['ai']['max_tokens']

# Get API key based on provider
if AI_PROVIDER == 'openai':
    AI_API_KEY = os.getenv(config['ai']['openai']['api_key_env'])
elif AI_PROVIDER == 'anthropic':
    AI_API_KEY = os.getenv(config['ai']['anthropic']['api_key_env'])
elif AI_PROVIDER == 'local':
    AI_API_KEY = None  # Local models don't need API keys
    AI_BASE_URL = config['ai']['local']['base_url']
else:
    raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")

# Scraping Configuration
USER_AGENT = config['scraping']['user_agent']
REQUEST_DELAY = config['scraping']['request_delay']
REQUEST_TIMEOUT = config['scraping']['request_timeout']
MAX_RETRIES = config['scraping']['max_retries']

# Processing Configuration
DESCRIPTION_LENGTH = config['processing']['description_length']
MAX_TAGS = config['processing']['max_tags']
BATCH_SIZE = config['processing']['batch_size']
EXTRACT_PEOPLE = config['processing']['extract_people']
EXTRACT_AUTHOR = config['processing']['extract_author']
EXTRACT_PUBLISHER = config['processing']['extract_publisher']

# Output Configuration
OUTPUT_FORMAT = config['output']['format']
OUTPUT_DELIMITER = config['output']['delimiter']
RESUME_PROCESSING = config['output']['resume_processing']