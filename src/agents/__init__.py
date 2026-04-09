"""Agents package initialization."""

from agents.data_analyst import DataAnalystAgent      # ← remove src.
from agents.product_manager import ProductManagerAgent
from agents.marketing import MarketingAgent
from agents.risk_critic import RiskCriticAgent

__all__ = [
    "DataAnalystAgent",
    "ProductManagerAgent", 
    "MarketingAgent",
    "RiskCriticAgent",
]