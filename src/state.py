"""State management for the interview workflow."""
from typing import Dict, Any, List
from dataclasses import dataclass, field
from langgraph.graph import State

@dataclass
class InterviewState(State):
    """Interview state management with LangGraph integration."""
    messages: List[Dict[str, str]] = field(default_factory=list)
    current_phase: str = "initial"
    completed_phases: List[str] = field(default_factory=list)
    collected_insights: Dict[str, Dict] = field(default_factory=lambda: {
        "learning_style": {},
        "career_goals": {},
        "skills": {},
        "initial_insights": {}
    })

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access to state attributes."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Dict-like setter for state attributes."""
        if not hasattr(self, key):
            print(f"WARNING: Setting unknown state field: {key}")
        setattr(self, key, value)

    def dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for LangGraph."""
        return {
            "messages": self.messages,
            "current_phase": self.current_phase,
            "completed_phases": self.completed_phases,
            "collected_insights": self.collected_insights
        }

    def copy(self) -> 'InterviewState':
        """Create a deep copy of the state for LangGraph."""
        from copy import deepcopy
        return InterviewState(
            messages=deepcopy(self.messages),
            current_phase=self.current_phase,
            completed_phases=deepcopy(self.completed_phases),
            collected_insights=deepcopy(self.collected_insights)
        )

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update state from dictionary with validation and error tracking."""
        try:
            for key, value in data.items():
                if not hasattr(self, key):
                    print(f"WARNING: Attempting to set unknown state field: {key}")
                    continue

                if key == "current_phase":
                    if value not in ["initial", "learning_style", "career_goals", "skills_assessment", "complete"]:
                        raise ValueError(f"Invalid phase: {value}")
                    if value not in self.completed_phases:
                        self.completed_phases.append(self.current_phase)

                elif key == "collected_insights":
                    if not isinstance(value, dict):
                        raise ValueError("collected_insights must be a dictionary")
                    for insight_key, insight_value in value.items():
                        if insight_key not in self.collected_insights:
                            print(f"WARNING: Unknown insight key: {insight_key}")
                            continue
                        self.collected_insights[insight_key].update(insight_value)
                        continue

                self.set(key, value)
                print(f"DEBUG: Updated state field {key}: {value}")
        except Exception as e:
            print(f"ERROR updating state: {str(e)}")
            print(f"Current state before error: {self.__dict__}")
            raise

    def add_message(self, message: Dict[str, str]) -> None:
        """Add message to state with validation."""
        if isinstance(message, dict) and "role" in message and "content" in message:
            self.messages.append(message)

    def get_last_message(self) -> Dict[str, str]:
        """Get last message from state safely."""
        return self.messages[-1] if self.messages else {}
