"""Base agent setup with LangChain."""

from typing import List, Optional, Dict, Any, Callable
from langchain_core.tools import BaseTool, StructuredTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import settings


class BaseAgent:
    """Base class for all war room agents using LangChain."""
    
    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        config_key: str,
        tools: Optional[List] = None,
        verbose: bool = True
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.config_key = config_key
        self.tools = tools or []
        self.verbose = verbose
        
        # Get LLM from settings
        self.llm = settings.get_llm(config_key)
    
    def run_tools(self, tool_inputs: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
        """Run tools with given inputs and return results."""
        results = {}
        for tool_name, params in tool_inputs.items():
            # Find the tool
            tool = next((t for t in self.tools if getattr(t, 'name', None) == tool_name), None)
            if tool:
                try:
                    if isinstance(tool, StructuredTool):
                        result = tool.invoke(params)
                    else:
                        result = tool._run(**params)
                    results[tool_name] = result
                except Exception as e:
                    results[tool_name] = f"Error: {str(e)}"
            else:
                results[tool_name] = f"Tool {tool_name} not found"
        return results
    
    def analyze_with_llm(self, prompt: str) -> str:
     """Run LLM with system context."""
    # FIX: Must include word "json" for response_format to work with Groq
     json_prompt = f"{prompt}\n\nProvide your response in JSON format."
    
     messages = [
        SystemMessage(content=f"You are {self.role}. {self.goal}\n\n{self.backstory}"),
        HumanMessage(content=json_prompt)
     ]
    
     try:
        response = self.llm.invoke(messages)
        return response.content if hasattr(response, 'content') else str(response)
     except Exception as e:
        if self.verbose:
            print(f"LLM Error: {e}")
        return f"Error in analysis: {str(e)}"
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses for structured analysis."""
        raise NotImplementedError("Subclasses must implement analyze()")