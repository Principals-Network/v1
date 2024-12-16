"""LangGraph workflow for user profiling system."""
from typing import Dict, Any, List
from langgraph.graph import Graph, StateGraph, END
from src.agents.specialized import (
    InterviewCoordinatorAgent,
    LearningStyleAnalyzerAgent,
    CareerPathAnalyzerAgent,
    InsightAggregatorAgent
)

class InterviewState:
    """Interview state management with dict-like access."""
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.current_phase: str = "initial"
        self.completed_phases: List[str] = []
        self.collected_insights: Dict[str, Dict] = {
            "learning_style": {},
            "career_goals": {},
            "skills": {}
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access to state attributes."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Dict-like setter for state attributes."""
        setattr(self, key, value)

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update state from dictionary with validation."""
        try:
            for key, value in data.items():
                if hasattr(self, key):
                    self.set(key, value)
                    if key == "current_phase" and value not in self.completed_phases:
                        self.completed_phases.append(value)
        except Exception as e:
            print(f"Error updating state: {str(e)}")

    def add_message(self, message: Dict[str, str]) -> None:
        """Add message to state with validation."""
        if isinstance(message, dict) and "role" in message and "content" in message:
            self.messages.append(message)

    def get_last_message(self) -> Dict[str, str]:
        """Get last message from state safely."""
        return self.messages[-1] if self.messages else {}

def create_interview_workflow(mock_responses: bool = True) -> Graph:
    """Create the interview workflow graph."""
    coordinator = InterviewCoordinatorAgent(mock_responses=mock_responses)
    learning_analyzer = LearningStyleAnalyzerAgent(mock_responses=mock_responses)
    career_analyzer = CareerPathAnalyzerAgent(mock_responses=mock_responses)
    aggregator = InsightAggregatorAgent(mock_responses=mock_responses)

    workflow = StateGraph(InterviewState)

    # Add nodes for each agent
    workflow.add_node("coordinator", coordinator.generate_response)
    workflow.add_node("learning_analyzer", learning_analyzer.analyze_response)
    workflow.add_node("career_analyzer", career_analyzer.create_roadmap)
    workflow.add_node("aggregator", aggregator.generate_report)

    # Define conditional routing functions
    def should_transition_to_learning(state: InterviewState) -> bool:
        return state.get("current_phase") == "learning_style"

    def should_transition_to_career(state: InterviewState) -> bool:
        return state.get("current_phase") == "career_goals"

    def should_transition_to_skills(state: InterviewState) -> bool:
        return state.get("current_phase") == "skills_assessment"

    def should_end_interview(state: InterviewState) -> bool:
        return state.get("current_phase") == "complete"

    # Add conditional edges for phase transitions
    workflow.add_conditional_edges(
        "coordinator",
        should_transition_to_learning,
        {
            True: "learning_analyzer",
            False: "coordinator"
        }
    )

    workflow.add_conditional_edges(
        "learning_analyzer",
        should_transition_to_career,
        {
            True: "career_analyzer",
            False: "coordinator"
        }
    )

    workflow.add_conditional_edges(
        "career_analyzer",
        should_transition_to_skills,
        {
            True: "aggregator",
            False: "coordinator"
        }
    )

    workflow.add_conditional_edges(
        "aggregator",
        should_end_interview,
        {
            True: END,  # Using LangGraph's END constant
            False: "coordinator"
        }
    )

    # Set the entry point
    workflow.set_entry_point("coordinator")

    return workflow.compile()
