"""
ATLAS Agent Runner - Simple Python Implementation

Runs ATLAS agent using OpenAI API directly.
This is a minimal implementation for testing - SuperOptiX integration comes later.
"""

import os
import yaml
from pathlib import Path
from openai import OpenAI
from typing import List, Dict
import json
from dotenv import load_dotenv

# Load environment variables from multiple possible locations
env_locations = [
    Path(__file__).parent / ".env",  # atlas/.env
    Path(__file__).parent.parent / ".env",  # project root .env
    Path(__file__).parent.parent / "config" / "api_keys.env",  # config/api_keys.env
]

for env_path in env_locations:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"INFO: Loaded environment from {env_path}")
        break

# Load atlas config
config_path = Path(__file__).parent / "atlas" / "agents" / "atlas.yaml"
with open(config_path) as f:
    config = yaml.safe_load(f)

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key == "your_openai_key":
    print("WARNING: No valid OPENAI_API_KEY found!")
    print("Please set your API key in one of these locations:")
    for loc in env_locations:
        print(f"  - {loc}")
    print("\nOr set the OPENAI_API_KEY environment variable")
    api_key = None

# Initialize OpenAI client
client = OpenAI(api_key=api_key) if api_key else None

class ATLASAgent:
    """Simple ATLAS agent implementation"""

    def __init__(self):
        self.config = config
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = config['system_prompt']
        self.model = config['model']['name']
        self.temperature = config['model']['temperature']
        self.max_tokens = config['model']['max_tokens']

    def chat(self, user_message: str) -> str:
        """Send a message to ATLAS and get response"""

        # Check if client is available
        if client is None:
            return "ERROR: OpenAI client not initialized. Please set OPENAI_API_KEY environment variable."

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Build messages for API call
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add conversation history (limit to max_context_length from config)
        max_context = config['conversation']['max_context_length']
        recent_history = self.conversation_history[-max_context:]
        messages.extend(recent_history)

        # Call OpenAI API
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            assistant_message = response.choices[0].message.content

            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

        except Exception as e:
            return f"ERROR: {str(e)}"

    def reset(self):
        """Reset conversation history"""
        self.conversation_history = []

    def get_greeting(self) -> str:
        """Get the greeting message"""
        return config['conversation']['greeting']


def test_atlas():
    """Quick test of ATLAS agent"""
    print("Starting ATLAS test...")
    print(f"Config loaded: {config['name']} v{config['version']}")
    print(f"Model: {config['model']['name']}")
    print()

    agent = ATLASAgent()

    print(f"ATLAS: {agent.get_greeting()}")
    print()

    # Test conversation
    test_messages = [
        "Hello! What is your name and purpose?",
        "Can you tell me what capabilities you have right now?",
    ]

    for msg in test_messages:
        print(f"User: {msg}")
        response = agent.chat(msg)
        print(f"ATLAS: {response}")
        print()


if __name__ == "__main__":
    test_atlas()
