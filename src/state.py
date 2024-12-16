"""State management for the interview workflow."""
from typing import Dict, Any, List, TypeVar, Optional, Iterator
from dataclasses import dataclass, field
from langgraph.state import State

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

    def __getitem__(self, key: str) -> Any:
        """Dict-like access for LangGraph compatibility."""
        try:
            return getattr(self, key)
        except AttributeError as e:
            print(f"ERROR in __getitem__: {str(e)}")
            raise KeyError(key) from e

    def __setitem__(self, key: str, value: Any) -> None:
        """Dict-like setter for LangGraph compatibility."""
        try:
            setattr(self, key, value)
        except Exception as e:
            print(f"ERROR in __setitem__: {str(e)}")
            raise

    def __contains__(self, key: str) -> bool:
        """Check if key exists in state."""
        return key in self.keys()

    def keys(self) -> Iterator[str]:
        """Return iterator of state keys for LangGraph compatibility."""
        return iter(["messages", "current_phase", "completed_phases", "collected_insights"])

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access to state attributes."""
        try:
            return self[key]
        except KeyError:
            return default

    def set(self, key: str, value: Any) -> None:
        """Dict-like setter for state attributes."""
        try:
            if key not in self.keys():
                print(f"WARNING: Setting unknown state field: {key}")
            self[key] = value
        except Exception as e:
            print(f"ERROR in set: {str(e)}")
            raise

    def dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for LangGraph."""
        try:
            return {key: self[key] for key in self.keys()}
        except Exception as e:
            print(f"ERROR in dict: {str(e)}")
            return {}

    def copy(self) -> 'InterviewState':
        """Create a deep copy of the state for LangGraph."""
        try:
            from copy import deepcopy
            return InterviewState(
                messages=deepcopy(self.messages),
                current_phase=self.current_phase,
                completed_phases=deepcopy(self.completed_phases),
                collected_insights=deepcopy(self.collected_insights)
            )
        except Exception as e:
            print(f"ERROR in copy: {str(e)}")
            raise

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update state from dictionary with validation and error tracking."""
        try:
            print(f"DEBUG: Updating state with data: {data}")
            for key, value in data.items():
                if key not in self.keys():
                    print(f"WARNING: Attempting to set unknown state field: {key}")
                    continue

                if key == "current_phase":
                    if value not in ["initial", "learning_style", "career_goals", "skills_assessment", "complete"]:
                        raise ValueError(f"Invalid phase: {value}")
                    if value not in self.completed_phases and self.current_phase != value:
                        self.completed_phases.append(self.current_phase)

                elif key == "collected_insights":
                    if not isinstance(value, dict):
                        raise ValueError("collected_insights must be a dictionary")
                    for insight_key, insight_value in value.items():
                        if insight_key not in self.collected_insights:
                            print(f"WARNING: Unknown insight key: {insight_key}")
                            continue
                        if isinstance(insight_value, dict):
                            self.collected_insights[insight_key].update(insight_value)
                        else:
                            print(f"WARNING: Invalid insight value type for {insight_key}: {type(insight_value)}")

                self[key] = value
                print(f"DEBUG: Updated state field {key}: {value}")

        except Exception as e:
            print(f"ERROR updating state: {str(e)}")
            print(f"Current state before error: {self.__dict__}")
            raise

    def add_message(self, message: Dict[str, str]) -> None:
        """Add message to state with validation."""
        try:
            if isinstance(message, dict) and "role" in message and "content" in message:
                self.messages.append(message)
                print(f"DEBUG: Added message: {message}")
            else:
                print(f"WARNING: Invalid message format: {message}")
        except Exception as e:
            print(f"ERROR in add_message: {str(e)}")
            raise

    def get_last_message(self) -> Dict[str, str]:
        """Get last message from state safely."""
        try:
            return self.messages[-1] if self.messages else {}
        except Exception as e:
            print(f"ERROR in get_last_message: {str(e)}")
            return {}
