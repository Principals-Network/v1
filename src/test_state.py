"""Test state management implementation."""
from .state import InterviewState, InterviewStateDict

def test_state_dict_conversion():
    """Test conversion between InterviewState and dict."""
    state = InterviewState()

    # Test initial state
    state_dict = state.dict()
    assert isinstance(state_dict, dict)
    assert all(key in state_dict for key in ["messages", "current_phase", "completed_phases", "collected_insights"])

    # Test state updates
    state.add_message({"role": "user", "content": "test message"})
    state.current_phase = "learning_style"
    state.completed_phases.append("initial")

    updated_dict = state.dict()
    assert len(updated_dict["messages"]) == 1
    assert updated_dict["current_phase"] == "learning_style"
    assert "initial" in updated_dict["completed_phases"]

if __name__ == "__main__":
    test_state_dict_conversion()
    print("All state tests passed!")
