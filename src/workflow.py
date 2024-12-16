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
            "skills": {},
            "initial_insights": {}  # Add this to match coordinator's insight key
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like access to state attributes."""
        return getattr(self, key, default)

    def set(self, key: str, value: Any) -> None:
        """Dict-like setter for state attributes."""
        setattr(self, key, value)

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

def create_interview_workflow(mock_responses: bool = True) -> Graph:
    """Create the interview workflow graph."""
    coordinator = InterviewCoordinatorAgent(mock_responses=mock_responses)
    learning_analyzer = LearningStyleAnalyzerAgent(mock_responses=mock_responses)
    career_analyzer = CareerPathAnalyzerAgent(mock_responses=mock_responses)
    aggregator = InsightAggregatorAgent(mock_responses=mock_responses)

    workflow = StateGraph(InterviewState)

    # Add nodes for each agent with specified output fields
    workflow.add_node("coordinator", coordinator.generate_response, output_fields=["messages", "current_phase", "collected_insights"])
    workflow.add_node("learning_analyzer", learning_analyzer.analyze_response, output_fields=["messages", "current_phase", "collected_insights"])
    workflow.add_node("career_analyzer", career_analyzer.create_roadmap, output_fields=["messages", "current_phase", "collected_insights"])
    workflow.add_node("aggregator", aggregator.generate_report, output_fields=["messages", "current_phase", "collected_insights"])

    # Define conditional routing functions with validation
    def should_transition_to_learning(state: InterviewState) -> bool:
        """Validate and check transition to learning style phase."""
        current = state.get("current_phase")
        return current == "initial" and state.get("collected_insights", {}).get("initial_insights")

    def should_transition_to_career(state: InterviewState) -> bool:
        """Validate and check transition to career goals phase."""
        current = state.get("current_phase")
        return current == "learning_style" and state.get("collected_insights", {}).get("learning_style")

    def should_transition_to_skills(state: InterviewState) -> bool:
        """Validate and check transition to skills assessment phase."""
        current = state.get("current_phase")
        return current == "career_goals" and state.get("collected_insights", {}).get("career_goals")

    def should_end_interview(state: InterviewState) -> bool:
        """Validate and check if interview should end."""
        current = state.get("current_phase")
        return current == "skills_assessment" and state.get("collected_insights", {}).get("skills")

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
