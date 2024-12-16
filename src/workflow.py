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
    def should_transition_to_learning(state: InterviewState) -> str:
        """Validate and check transition to learning style phase."""
        try:
            current = state["current_phase"]
            insights = state["collected_insights"]
            if (current == "initial" and
                isinstance(insights.get("initial_insights"), dict) and
                bool(insights.get("initial_insights"))):
                return "learning_analyzer"
            return "coordinator"
        except Exception as e:
            print(f"ERROR in should_transition_to_learning: {str(e)}")
            return "coordinator"

    def should_transition_to_career(state: InterviewState) -> str:
        """Validate and check transition to career goals phase."""
        try:
            current = state["current_phase"]
            insights = state["collected_insights"]
            if (current == "learning_style" and
                isinstance(insights.get("learning_style"), dict) and
                bool(insights.get("learning_style"))):
                return "career_analyzer"
            return "coordinator"
        except Exception as e:
            print(f"ERROR in should_transition_to_career: {str(e)}")
            return "coordinator"

    def should_transition_to_skills(state: InterviewState) -> str:
        """Validate and check transition to skills assessment phase."""
        try:
            current = state["current_phase"]
            insights = state["collected_insights"]
            if (current == "career_goals" and
                isinstance(insights.get("career_goals"), dict) and
                bool(insights.get("career_goals"))):
                return "aggregator"
            return "coordinator"
        except Exception as e:
            print(f"ERROR in should_transition_to_skills: {str(e)}")
            return "coordinator"

    def should_end_interview(state: InterviewState) -> str:
        """Validate and check if interview should end."""
        try:
            current = state["current_phase"]
            insights = state["collected_insights"]
            required_insights = ["initial_insights", "learning_style", "career_goals", "skills"]

            print(f"DEBUG: Current phase: {current}")
            print(f"DEBUG: Collected insights: {insights}")
            print(f"DEBUG: Required insights: {required_insights}")

            has_all_insights = all(
                isinstance(insights.get(key), dict) and bool(insights.get(key))
                for key in required_insights
            )

            print(f"DEBUG: Has all insights: {has_all_insights}")
            print(f"DEBUG: Current phase check: {current == 'skills_assessment'}")

            if current == "skills_assessment" and has_all_insights:
                print("DEBUG: All conditions met, ending interview")
                return END

            print(f"DEBUG: Interview continuing. Phase: {current}, Has all insights: {has_all_insights}")
            return "coordinator"
        except Exception as e:
            print(f"ERROR in should_end_interview: {str(e)}")
            print(f"ERROR state dump: {state.dict()}")
            return "coordinator"

    # Add edges with proper return values
    workflow.add_edge("coordinator", should_transition_to_learning)
    workflow.add_edge("coordinator", should_transition_to_career)
    workflow.add_edge("coordinator", should_transition_to_skills)
    workflow.add_edge("coordinator", should_end_interview)

    workflow.add_edge("learning_analyzer", lambda x: "coordinator")
    workflow.add_edge("career_analyzer", lambda x: "coordinator")
    workflow.add_edge("aggregator", should_end_interview)  # Remove lambda wrapper to ensure proper state validation

    # Set the entry point
    workflow.set_entry_point("coordinator")

    return workflow.compile()
