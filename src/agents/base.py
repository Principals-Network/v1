"""Base agent classes and utilities for the user profiling system."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage

class AgentState(BaseModel):
    """Base state model for all agents with dict-like access."""
    messages: List[BaseMessage] = []
    current_phase: str = "initial"
    collected_insights: Dict[str, Any] = {}
    phase_completion: Dict[str, bool] = {
        "initial": False,
        "learning_style": False,
        "career_goals": False,
        "skills_assessment": False
    }

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access to state attributes."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Dict-like setter for state attributes with validation."""
        if key == "phase_completion" and not isinstance(value, dict):
            raise ValueError("phase_completion must be a dictionary")
        setattr(self, key, value)

    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the conversation history with validation."""
        if isinstance(message, BaseMessage):
            self.messages.append(message)

    def get_context(self) -> str:
        """Get formatted conversation context."""
        return "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in self.messages[-5:]  # Last 5 messages for recent context
        ])

class BaseAgent:
    """Base class for all agents in the interview system."""

    def __init__(
        self,
        name: str = "",
        system_prompt: str = "",
        state: Optional[AgentState] = None,
        mock_responses: bool = True
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.state = state or AgentState()
        self.mock_responses = mock_responses

    def get_system_message(self) -> SystemMessage:
        """Get the agent's system message."""
        return SystemMessage(content=self.system_prompt)

    def update_state(self, key: str, value: Any) -> None:
        """Update the agent's state with validation."""
        try:
            if key == "collected_insights":
                if not isinstance(value, dict):
                    raise ValueError("collected_insights must be a dictionary")
                if key not in self.state.collected_insights:
                    self.state.collected_insights[key] = {}
                self.state.collected_insights[key].update(value)
            elif key == "phase_completion":
                if not isinstance(value, dict):
                    raise ValueError("phase_completion must be a dictionary")
                self.state.phase_completion.update(value)
            else:
                self.state.set(key, value)
        except Exception as e:
            print(f"Error updating agent state: {str(e)}")

    def get_collected_insights(self) -> Dict[str, Any]:
        """Get all insights collected by the agent."""
        return self.state.collected_insights
