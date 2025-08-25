"""Utility functions used in our graph."""

import os
from langchain_anthropic import ChatAnthropic
from langchain.chat_models import init_chat_model



def split_model_and_provider(fully_specified_name: str) -> dict:
    """Initialize the configured chat model."""
    if "/" in fully_specified_name:
        provider, model = fully_specified_name.split("/", maxsplit=1)
    else:
        provider = None
        model = fully_specified_name
    return {"model": model, "provider": provider}


def get_llm(model: str) -> ChatAnthropic:
    model_info = split_model_and_provider(model)
    if model_info["provider"]:
        if model_info["provider"] == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required for Anthropic models")
            os.environ["ANTHROPIC_API_KEY"] = api_key
        
        llm = init_chat_model(
            model=model_info["model"], 
            model_provider=model_info["provider"]
        )
    else:
        llm = init_chat_model(model)
    
    return llm