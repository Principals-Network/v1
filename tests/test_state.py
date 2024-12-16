"""Test cases for state management."""
import pytest
from typing import Dict, Any
from src.state import InterviewState, state_reducer

def test_state_reducer():
    """Test state reducer function."""
    a = {"key1": "value1", "key2": "value2"}
    b = {"key2": "new_value", "key3": "value3"}
    result = state_reducer(a, b)
    assert result == {"key1": "value1", "key2": "new_value", "key3": "value3"}

def test_interview_state_initialization():
    """Test InterviewState initialization."""
    state = InterviewState()
    assert state["next"] == "coordinator"
    assert state["current_phase"] == "initial"
    assert isinstance(state["user_responses"], dict)
    assert isinstance(state["learning_style"], dict)
    assert isinstance(state["career_path"], dict)
    assert isinstance(state["insights"], list)
    assert state["report"] is None

def test_interview_state_dict_access():
    """Test dict-like access to InterviewState."""
    state = InterviewState()

    # Test __getitem__
    assert state["current_phase"] == "initial"

    # Test __setitem__
    state["current_phase"] = "learning"
    assert state["current_phase"] == "learning"

    # Test __contains__
    assert "current_phase" in state
    assert "nonexistent_key" not in state

    # Test get with default
    assert state.get("nonexistent_key", "default") == "default"

def test_interview_state_update():
    """Test state update functionality."""
    state = InterviewState()
    updates = {
        "current_phase": "career",
        "user_responses": {"question1": "answer1"},
        "insights": ["insight1"]
    }
    state.update(updates)

    assert state["current_phase"] == "career"
    assert state["user_responses"] == {"question1": "answer1"}
    assert state["insights"] == ["insight1"]

def test_interview_state_to_dict():
    """Test conversion to dictionary."""
    state = InterviewState()
    state_dict = state.to_dict()

    assert isinstance(state_dict, dict)
    assert all(key in state_dict for key in [
        "next", "current_phase", "user_responses", "learning_style",
        "career_path", "insights", "report"
    ])
