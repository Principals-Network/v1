"""Base agent classes and utilities for the user profiling system."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import BaseMessage
from langgraph.graph import END

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
    next: Optional[Union[str, type(END)]] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access to state attributes."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Dict-like setter for state attributes with validation."""
        if key == "phase_completion" and not isinstance(value, dict):
            raise ValueError("phase_completion must be a dictionary")
        if key == "next" and value is not None and not isinstance(value, (str, type(END))):
            raise ValueError(f"Invalid next value type: {type(value)}")
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
            elif key == "next" and value is not None and not isinstance(value, (str, type(END))):
                raise ValueError(f"Invalid next value type: {type(value)}")
            else:
                self.state.set(key, value)
        except Exception as e:
            print(f"Error updating agent state: {str(e)}")

    def get_collected_insights(self) -> Dict[str, Any]:
        """Get all insights collected by the agent."""
        return self.state.collected_insights

class InterviewCoordinator(BaseAgent):
    """Coordinates the overall interview process."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Interview Coordinator",
            system_prompt="You are an interview coordinator responsible for guiding the user through a learning profile assessment.",
            mock_responses=mock_responses
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current phase of the interview."""
        try:
            if self.mock_responses:
                # Preserve existing state and update with new information
                updated_state = state.copy()
                updated_state.update({
                    "messages": state.get("messages", []),
                    "current_phase": "learning_style",
                    "next": "learning_style",
                    "completed_phases": list(set(state.get("completed_phases", []) + ["initial"]))
                })
                return updated_state
            # Real implementation would go here
            return state
        except Exception as e:
            print(f"ERROR in InterviewCoordinator process: {str(e)}")
            return state

class LearningStyleAnalyzer(BaseAgent):
    """Analyzes the user's learning style preferences."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Learning Style Analyzer",
            system_prompt="You are an expert in analyzing learning styles and educational preferences.",
            mock_responses=mock_responses
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process learning style analysis."""
        try:
            if self.mock_responses:
                # Preserve existing state and update with new information
                updated_state = state.copy()
                updated_state.update({
                    "messages": state.get("messages", []),
                    "learning_style": {"primary_style": "hands-on"},
                    "current_phase": "career_path",
                    "next": "career_path",
                    "completed_phases": list(set(state.get("completed_phases", []) + ["learning_style"]))
                })
                return updated_state
            # Real implementation would go here
            return state
        except Exception as e:
            print(f"ERROR in LearningStyleAnalyzer process: {str(e)}")
            return state

class CareerPathAnalyzer(BaseAgent):
    """Analyzes career goals and provides recommendations."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Career Path Analyzer",
            system_prompt="You are an expert in career development and professional growth analysis.",
            mock_responses=mock_responses
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process career path analysis."""
        try:
            if self.mock_responses:
                # Preserve existing state and update with new information
                updated_state = state.copy()
                updated_state.update({
                    "messages": state.get("messages", []),
                    "career_path": {"suggested_path": "software-architect"},
                    "current_phase": "aggregate",
                    "next": "aggregate",
                    "completed_phases": list(set(state.get("completed_phases", []) + ["career_path"]))
                })
                return updated_state
            # Real implementation would go here
            return state
        except Exception as e:
            print(f"ERROR in CareerPathAnalyzer process: {str(e)}")
            return state

class InsightAggregator(BaseAgent):
    """Aggregates insights from all phases and generates final recommendations."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Insight Aggregator",
            system_prompt="You are responsible for combining all insights to create personalized learning recommendations.",
            mock_responses=mock_responses
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process insight aggregation."""
        try:
            if self.mock_responses:
                # Preserve existing state and update with new information
                updated_state = state.copy()
                updated_state.update({
                    "messages": state.get("messages", []),
                    "collected_insights": {
                        "learning_profile": state.get("learning_style", {}),
                        "career_goals": state.get("career_path", {}),
                    },
                    "current_phase": "complete",
                    "next": END,
                    "completed_phases": list(set(state.get("completed_phases", []) + ["aggregate"]))
                })
                return updated_state
            # Real implementation would go here
            return state
        except Exception as e:
            print(f"ERROR in InsightAggregator process: {str(e)}")
            return state
