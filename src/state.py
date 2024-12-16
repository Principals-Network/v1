"""State management for the interview system."""
from typing import Dict, Any, TypedDict, Optional, List, Iterator
from typing_extensions import Annotated

def state_reducer(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer function for merging state updates."""
    return {**a, **b}

class InterviewStateDict(TypedDict):
    """TypedDict for interview state with reducer annotation."""
    next: str
    current_phase: str
    message: Optional[str]
    messages: Annotated[List[Dict[str, str]], state_reducer]
    user_responses: Annotated[Dict[str, Any], state_reducer]
    learning_style: Annotated[Dict[str, Any], state_reducer]
    career_path: Annotated[Dict[str, Any], state_reducer]
    insights: Annotated[List[str], state_reducer]
    report: Optional[Dict[str, Any]]
    completed_phases: Annotated[List[str], state_reducer]
    session_id: Optional[str]

class InterviewState:
    """State management class for the interview workflow."""
    def __init__(self, state_dict: Optional[Dict[str, Any]] = None):
        self._state: InterviewStateDict = {
            "next": "coordinator",
            "current_phase": "initial",
            "message": None,
            "messages": [],
            "user_responses": {},
            "learning_style": {},
            "career_path": {},
            "insights": [],
            "report": None,
            "completed_phases": [],
            "session_id": None
        }
        if state_dict is not None:
            self.update(state_dict)

    def __getitem__(self, key: str) -> Any:
        """Dict-like access for LangGraph compatibility."""
        return self._state[key]

    def __setitem__(self, key: str, value: Any) -> None:
        """Dict-like setter for LangGraph compatibility."""
        self._state[key] = value

    def __contains__(self, key: str) -> bool:
        """Support for 'in' operator."""
        return key in self._state

    def get(self, key: str, default: Any = None) -> Any:
        """Get value from state with default."""
        return self._state.get(key, default)

    def update(self, updates: Dict[str, Any]) -> None:
        """Update state with new values."""
        self._state.update(updates)

    def to_dict(self) -> InterviewStateDict:
        """Convert state to dictionary."""
        return self._state

    def keys(self) -> Iterator[str]:
        """Return iterator of state keys."""
        return iter(self._state.keys())
