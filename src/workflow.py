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
            lambda _: True: END
        }
    )

    # Set the entry point
    workflow.set_entry_point("coordinator")

    return workflow.compile()
