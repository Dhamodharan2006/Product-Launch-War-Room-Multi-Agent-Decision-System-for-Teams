"""Persistent trace logging for agent execution without external dependencies."""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class ExecutionTracer:
    """Captures and persists agent execution traces to local files."""
    
    def __init__(self, output_dir: str = "./traces"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_trace: List[Dict[str, Any]] = []
        self.start_time: Optional[float] = None
        
    def start_trace(self, run_id: str, inputs: Dict[str, Any]):
        """Initialize a new execution trace."""
        self.start_time = time.time()
        self.current_trace = [{
            "timestamp": datetime.now().isoformat(),
            "event": "trace_start",
            "run_id": run_id,
            "inputs": inputs,
            "agent": "system",
            "duration_ms": 0
        }]
        
    def log_agent_start(self, agent_name: str, inputs: Dict[str, Any]):
        """Log agent execution start."""
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": "agent_start",
            "agent": agent_name,
            "inputs": self._sanitize(inputs),
            "duration_ms": self._elapsed()
        })
        
    def log_agent_end(self, agent_name: str, outputs: Dict[str, Any], tools_used: List[str] = None):
        """Log agent execution completion."""
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": "agent_end",
            "agent": agent_name,
            "outputs": self._sanitize(outputs),
            "tools_used": tools_used or [],
            "duration_ms": self._elapsed()
        })
        
    def log_tool_call(self, tool_name: str, inputs: Dict[str, Any], output: Any, error: Optional[str] = None):
        """Log tool invocation with full I/O."""
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": "tool_call",
            "tool": tool_name,
            "inputs": self._sanitize(inputs),
            "output": self._sanitize_output(output),
            "error": error,
            "duration_ms": self._elapsed()
        })
        
    def log_llm_call(self, agent_name: str, prompt: str, response: str, model: str, tokens_used: int = 0):
        """Log LLM interaction."""
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": "llm_call",
            "agent": agent_name,
            "model": model,
            "prompt_preview": prompt[:500] if prompt else None,
            "response_preview": response[:500] if response else None,
            "tokens_used": tokens_used,
            "duration_ms": self._elapsed()
        })
        
    def log_decision(self, decision: str, confidence: float, rationale: Dict[str, Any]):
        """Log final decision with full rationale."""
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": "final_decision",
            "decision": decision,
            "confidence": confidence,
            "rationale": rationale,
            "duration_ms": self._elapsed()
        })
        
    def end_trace(self, final_state: Dict[str, Any]):
        """Finalize and save trace to file."""
        total_duration = (time.time() - self.start_time) * 1000 if self.start_time else 0
        
        self.current_trace.append({
            "timestamp": datetime.now().isoformat(),
            "event": "trace_end",
            "total_duration_ms": total_duration,
            "final_state": self._sanitize(final_state)
        })
        
        # Save to file
        run_id = self.current_trace[0].get("run_id", "unknown")
        filename = f"trace_{run_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        
        trace_data = {
            "metadata": {
                "version": "1.0",
                "total_events": len(self.current_trace),
                "total_duration_ms": total_duration,
                "saved_at": datetime.now().isoformat()
            },
            "execution_trace": self.current_trace
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(trace_data, f, indent=2, default=str)
            
        # Also save latest trace as sample for repo
        sample_path = self.output_dir / "sample_trace.json"
        with open(sample_path, 'w', encoding='utf-8') as f:
            json.dump(trace_data, f, indent=2, default=str)
            
        return filepath
        
    def _elapsed(self) -> int:
        """Calculate elapsed time in milliseconds."""
        if not self.start_time:
            return 0
        return int((time.time() - self.start_time) * 1000)
        
    def _sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from trace."""
        if not isinstance(data, dict):
            return data
            
        sanitized = {}
        for key, value in data.items():
            # Skip sensitive keys
            if any(sensitive in key.lower() for sensitive in ['api_key', 'token', 'password', 'secret']):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize(v) if isinstance(v, dict) else v for v in value[:10]]  # Limit list size
            else:
                sanitized[key] = value
        return sanitized
        
    def _sanitize_output(self, output: Any) -> Any:
        """Truncate large outputs."""
        if isinstance(output, str) and len(output) > 1000:
            return output[:1000] + "... [truncated]"
        return output


# Global tracer instance
tracer = ExecutionTracer()