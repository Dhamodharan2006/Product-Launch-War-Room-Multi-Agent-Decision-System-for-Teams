"""Configuration management with dynamic settings and .env persistence."""

import os
from dataclasses import dataclass, asdict
from typing import Dict, Optional, Any
from dotenv import load_dotenv, set_key
from pathlib import Path

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM models."""
    model: str
    temperature: float = 0.1
    max_tokens: int = 2000
    response_format: Optional[Dict[str, str]] = None


@dataclass
class ThresholdConfig:
    """Business logic thresholds for anomaly detection."""
    z_score_threshold: float = 2.0
    crash_rate_max: float = 2.0
    payment_success_min: float = 97.0
    api_latency_max: float = 300.0
    risk_score_emergency: float = 0.7
    risk_score_pause: float = 0.5


class Settings:
    """Application settings singleton with UI update capabilities."""
    
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
    
    # Threshold configuration
    THRESHOLDS = ThresholdConfig()
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "product-launch-war-room")
    
    # App Configuration
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    CHECKPOINT_DIR = os.getenv("CHECKPOINT_DIR", "./checkpoints")
    TRACES_DIR = os.getenv("TRACES_DIR", "./traces")
    
    @classmethod
    def get_llm(cls, role: str):
        """Get configured LLM for specific role."""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in environment")
        
        config = cls.MODEL_CONFIG.get(role)
        if not config:
            raise ValueError(f"No config found for role: {role}")
        
        from langchain_groq import ChatGroq
        
        return ChatGroq(
            api_key=cls.GROQ_API_KEY,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            model_kwargs={"response_format": config.response_format} if config.response_format else {}
        )
    
    @classmethod
    def update_model_config(cls, role: str, model: str = None, temperature: float = None, max_tokens: int = None):
        """Update model configuration for a specific role."""
        if role not in cls.MODEL_CONFIG:
            raise ValueError(f"Unknown role: {role}")
        
        config = cls.MODEL_CONFIG[role]
        if model:
            config.model = model
        if temperature is not None:
            config.temperature = temperature
        if max_tokens:
            config.max_tokens = max_tokens
    
    @classmethod
    def update_thresholds(cls, **kwargs):
        """Update threshold values."""
        for key, value in kwargs.items():
            if hasattr(cls.THRESHOLDS, key):
                setattr(cls.THRESHOLDS, key, value)
    
    @classmethod
    def save_to_env(cls, env_path: str = ".env"):
        """Save current configuration to .env file."""
        env_file = Path(env_path)
        
        # Ensure file exists
        env_file.touch(exist_ok=True)
        
        # Save API keys
        if cls.GROQ_API_KEY:
            set_key(env_file, "GROQ_API_KEY", cls.GROQ_API_KEY)
        if cls.LANGCHAIN_API_KEY:
            set_key(env_file, "LANGCHAIN_API_KEY", cls.LANGCHAIN_API_KEY)
        set_key(env_file, "LANGCHAIN_PROJECT", cls.LANGCHAIN_PROJECT)
        set_key(env_file, "ENVIRONMENT", cls.ENVIRONMENT)
        
        # Save thresholds
        for key, value in asdict(cls.THRESHOLDS).items():
            set_key(env_file, key.upper(), str(value))
        
        return True
    
    @classmethod
    def reload_from_env(cls, env_path: str = ".env"):
        """Reload configuration from .env file."""
        load_dotenv(env_path, override=True)
        cls.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        cls.LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
        cls.LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "product-launch-war-room")
        
        # Reload thresholds
        cls.THRESHOLDS.z_score_threshold = float(os.getenv("Z_SCORE_THRESHOLD", 2.0))
        cls.THRESHOLDS.crash_rate_max = float(os.getenv("CRASH_RATE_MAX", 2.0))
        cls.THRESHOLDS.payment_success_min = float(os.getenv("PAYMENT_SUCCESS_MIN", 97.0))
        cls.THRESHOLDS.api_latency_max = float(os.getenv("API_LATENCY_MAX", 300.0))
        cls.THRESHOLDS.risk_score_emergency = float(os.getenv("RISK_SCORE_EMERGENCY", 0.7))
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist."""
        os.makedirs(cls.CHECKPOINT_DIR, exist_ok=True)
        os.makedirs(cls.TRACES_DIR, exist_ok=True)
        os.makedirs("./outputs", exist_ok=True)
    
    @classmethod
    def get_threshold_dict(cls) -> Dict[str, float]:
        """Get thresholds as dictionary for tools."""
        return asdict(cls.THRESHOLDS)


settings = Settings()