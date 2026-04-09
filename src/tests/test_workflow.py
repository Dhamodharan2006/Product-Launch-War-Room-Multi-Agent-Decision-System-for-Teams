"""End-to-end workflow integration tests."""

import pytest
from src.graph.workflow import run_war_room
from src.data.mock_data import generate_metrics, generate_feedback, generate_release_notes


class TestEndToEndWorkflow:
    """Test complete system execution."""
    
    def test_full_workflow_execution(self):
        """Test that the full workflow executes without errors."""
        metrics = generate_metrics(days=14)
        feedback = generate_feedback(count=20)
        release_notes = generate_release_notes()
        
        result = run_war_room(metrics, feedback, release_notes, thread_id="test_001")
        
        assert result is not None
        assert "decision" in result
        assert result["decision"] in ["Proceed", "Pause", "Roll Back"]
        assert "rationale" in result
        assert "confidence_score" in result
        
    def test_decision_rationale_structure(self):
        """Test that decision rationale is properly structured."""
        metrics = generate_metrics()
        feedback = generate_feedback()
        release_notes = generate_release_notes()
        
        result = run_war_room(metrics, feedback, release_notes, thread_id="test_002")
        
        rationale = result.get("rationale", {})
        assert "key_drivers" in rationale
        assert "metric_references" in rationale
        assert "feedback_summary" in rationale
        assert isinstance(rationale["key_drivers"], list)
        
    def test_action_plan_structure(self):
        """Test that action plan has required fields."""
        metrics = generate_metrics()
        feedback = generate_feedback()
        release_notes = generate_release_notes()
        
        result = run_war_room(metrics, feedback, release_notes, thread_id="test_003")
        
        action_plan = result.get("action_plan", {})
        assert "next_24_48_hours" in action_plan
        assert isinstance(action_plan["next_24_48_hours"], list)
        
        if action_plan["next_24_48_hours"]:
            action = action_plan["next_24_48_hours"][0]
            assert "action" in action
            assert "owner" in action
            assert "due_hours" in action


if __name__ == "__main__":
    pytest.main([__file__, "-v"])