"""Configuration management and LLM initialization."""

import os
from dataclasses import dataclass
from typing import Dict, Optional, Any

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM models."""
    model: str
    temperature: float = 0.1
    max_tokens: int = 2000
    response_format: Optional[Dict[str, str]] = None


class Settings:
    """Application settings singleton."""
    
    # LLM Configurations per agent role
    MODEL_CONFIG: Dict[str, LLMConfig] = {
        "data_analyst": LLMConfig(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=2000,
            response_format={"type": "json_object"}
        ),
        "marketing": LLMConfig(
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=1500,
            response_format={"type": "json_object"}
        ),
        "risk_critic": LLMConfig(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=2000,
            response_format={"type": "json_object"}
        ),
        "devops_engineer": LLMConfig(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=1500,
            response_format={"type": "json_object"}
        ),
        "pm_orchestrator": LLMConfig(
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
    }
    
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    CHECKPOINT_DIR = os.getenv("CHECKPOINT_DIR", "./checkpoints")
    
    @classmethod
    def get_llm(cls, role: str) -> BaseChatModel:
        """Get configured LLM for specific role."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")
        
        config = cls.MODEL_CONFIG.get(role)
        if not config:
            raise ValueError(f"No config found for role: {role}")
        
        return ChatGroq(
            api_key=cls.GROQ_API_KEY,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            model_kwargs={"response_format": config.response_format} if config.response_format else {}
        )
    
    @classmethod
    def ensure_checkpoint_dir(cls):
        """Ensure checkpoint directory exists."""
        os.makedirs(cls.CHECKPOINT_DIR, exist_ok=True)


settings = Settings()