"""
LLM Configuration Utility
Provides a centralized way to configure LLM instances for LM Studio local models
"""

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LM Studio configuration
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "qwen/qwen3-4b-2507")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")  # Placeholder, not required by LM Studio


def get_local_llm(temperature=0.7, model=None, base_url=None, streaming=False):
    """
    Get LM Studio local LLM instance
    
    Args:
        temperature: Temperature for the model (default: 0.7)
        model: Model name (default: from env or "qwen/qwen3-4b-2507")
        base_url: Base URL for LM Studio API (default: from env or "http://localhost:1234/v1")
        streaming: Enable streaming responses (default: False)
    
    Returns:
        ChatOpenAI instance configured for LM Studio
    """
    return ChatOpenAI(
        base_url=base_url or LM_STUDIO_BASE_URL,
        model=model or LM_STUDIO_MODEL,
        temperature=temperature,
        api_key=LM_STUDIO_API_KEY,
        streaming=streaming
    )

