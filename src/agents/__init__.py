"""Agents package initialization."""

from src.agents.data_analyst import DataAnalystAgent      # ← remove src.
from src.agents.product_manager import ProductManagerAgent
from src.agents.marketing import MarketingAgent
from src.agents.risk_critic import RiskCriticAgent

__all__ = [
    "DataAnalystAgent",
    "ProductManagerAgent", 
    "MarketingAgent",
    "RiskCriticAgent",
]