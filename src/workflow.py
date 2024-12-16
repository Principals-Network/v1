"""LangGraph workflow for user profiling system."""
from typing import Dict, Any, List, TypeVar, Optional
from langgraph.graph import Graph, StateGraph, END
from src.agents.specialized import (
    InterviewCoordinatorAgent,
    LearningStyleAnalyzerAgent,
    CareerPathAnalyzerAgent,
    InsightAggregatorAgent
)
from src.state import InterviewState

def create_interview_workflow(mock_responses: bool = True) -> Graph:
    """Create the interview workflow graph."""
    coordinator = InterviewCoordinatorAgent(mock_responses=mock_responses)
    learning_analyzer = LearningStyleAnalyzerAgent(mock_responses=mock_responses)
    career_analyzer = CareerPathAnalyzerAgent(mock_responses=mock_responses)
    aggregator = InsightAggregatorAgent(mock_responses=mock_responses)

    # Create workflow with state validation
    workflow = StateGraph(InterviewState)

    # Add nodes for each agent
    workflow.add_node("coordinator", coordinator.generate_response)
    workflow.add_node("learning_analyzer", learning_analyzer.analyze_response)
    workflow.add_node("career_analyzer", career_analyzer.create_roadmap)
    workflow.add_node("aggregator", aggregator.generate_report)

    # Define conditional routing functions with validation
    def should_transition_to_learning(state: Dict) -> bool:
        """Validate and check transition to learning style phase."""
        try:
            current = state.get("current_phase")
            insights = state.get("collected_insights", {})
            return (current == "initial" and
                   isinstance(insights.get("initial_insights"), dict) and
                   bool(insights.get("initial_insights")))
        except Exception as e:
            print(f"ERROR in should_transition_to_learning: {str(e)}")
            return False

    def should_transition_to_career(state: Dict) -> bool:
        """Validate and check transition to career goals phase."""
        try:
            current = state.get("current_phase")
            insights = state.get("collected_insights", {})
            return (current == "learning_style" and
                   isinstance(insights.get("learning_style"), dict) and
                   bool(insights.get("learning_style")))
        except Exception as e:
            print(f"ERROR in should_transition_to_career: {str(e)}")
            return False

    def should_transition_to_skills(state: Dict) -> bool:
        """Validate and check transition to skills assessment phase."""
        try:
            current = state.get("current_phase")
            insights = state.get("collected_insights", {})
            return (current == "career_goals" and
                   isinstance(insights.get("career_goals"), dict) and
                   bool(insights.get("career_goals")))
        except Exception as e:
            print(f"ERROR in should_transition_to_skills: {str(e)}")
            return False

    def should_end_interview(state: Dict) -> bool:
        """Validate and check if interview should end."""
        try:
            current = state.get("current_phase")
            insights = state.get("collected_insights", {})
            required_insights = ["learning_style", "career_goals", "skills"]
            has_all_insights = all(
                isinstance(insights.get(key), dict) and bool(insights.get(key))
                for key in required_insights
            )
            return current == "skills_assessment" and has_all_insights
        except Exception as e:
            print(f"ERROR in should_end_interview: {str(e)}")
            return False

    # Add conditional edges for phase transitions
    workflow.add_conditional_edges(
        "coordinator",
        {
            should_transition_to_learning: "learning_analyzer",
            should_transition_to_career: "career_analyzer",
            should_transition_to_skills: "aggregator",
            should_end_interview: END
        }
    )

    workflow.add_conditional_edges(
        "learning_analyzer",
        {
            lambda _: True: "coordinator"
        }
    )

    workflow.add_conditional_edges(
        "career_analyzer",
        {
            lambda _: True: "coordinator"
        }
    )

    workflow.add_conditional_edges(
        "aggregator",
        {
            should_end_interview: END,
            lambda _: True: "coordinator"
        }
    )

    # Set the entry point
    workflow.set_entry_point("coordinator")

    return workflow.compile()
