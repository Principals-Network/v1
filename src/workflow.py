"""Interview workflow implementation using LangGraph."""
from typing import Dict, Any, List, TypedDict, Annotated
import traceback
from langgraph.graph import StateGraph, END

class InterviewState(TypedDict):
    """Type definition for interview state."""
    current_phase: str
    messages: List[Dict[str, str]]
    completed_phases: List[str]
    collected_insights: Dict[str, Any]
    learning_style: Dict[str, Any]
    career_path: Dict[str, Any]
    next: str

from src.agents.base import (
    InterviewCoordinator,
    LearningStyleAnalyzer,
    CareerPathAnalyzer,
    InsightAggregator
)

def should_continue(state: Dict[str, Any]) -> bool:
    """Check if the interview should continue."""
    return not should_end_interview(state)

def should_end_interview(state: Dict[str, Any]) -> bool:
    """
    Determine if the interview should end based on state conditions.

    Returns:
        bool: True if interview should end, False otherwise.
    """
    try:
        # Initialize state if needed
        state.setdefault('completed_phases', [])
        state.setdefault('collected_insights', {})
        state.setdefault('learning_style', {})
        state.setdefault('career_path', {})
        state.setdefault('current_phase', 'initial')

        # Check if we have all required data
        has_learning_style = bool(state.get("learning_style", {}).get("primary_style"))
        has_career_path = bool(state.get("career_path", {}).get("suggested_path"))
        has_insights = bool(state.get("collected_insights"))

        # Check phase completion
        completed_phases = set(state.get("completed_phases", []))
        required_phases = {"initial", "learning_style", "career_path", "aggregate"}
        current_phase = state.get("current_phase")

        # Only end if we're in aggregate or complete phase and all requirements are met
        if current_phase in ["aggregate", "complete"]:
            all_phases_completed = required_phases.issubset(completed_phases)
            should_end = (
                has_learning_style and
                has_career_path and
                has_insights and
                all_phases_completed
            )
        else:
            should_end = False

        print(f"DEBUG: Should end interview? {should_end}")
        print(f"DEBUG: Current phase: {current_phase}")
        print(f"DEBUG: Has learning style: {has_learning_style}")
        print(f"DEBUG: Has career path: {has_career_path}")
        print(f"DEBUG: Has insights: {has_insights}")
        print(f"DEBUG: Completed phases: {completed_phases}")
        print(f"DEBUG: All phases completed: {all_phases_completed if current_phase in ['aggregate', 'complete'] else False}")

        return should_end

    except Exception as e:
        print(f"ERROR in should_end_interview: {str(e)}")
        traceback.print_exc()
        return False

async def process_coordinator(state: Dict[str, Any], agent: InterviewCoordinator) -> Dict[str, Any]:
    """Process the coordinator phase."""
    try:
        print("\nDEBUG: Processing coordinator phase")
        result = await agent.process(state)

        # Ensure proper phase transition
        if "initial" not in result.get("completed_phases", []):
            result.setdefault("completed_phases", []).append("initial")

        # Force learning_style as next phase from coordinator
        result["next"] = "learning_style"
        result["current_phase"] = "learning_style"

        return result
    except Exception as e:
        print(f"ERROR in process_coordinator: {str(e)}")
        traceback.print_exc()
        return {
            "message": "Error in coordinator phase",
            "next": "learning_style",
            "current_phase": state.get("current_phase", "initial")
        }

async def process_learning(state: Dict[str, Any], agent: LearningStyleAnalyzer) -> Dict[str, Any]:
    """Process the learning style analysis phase."""
    try:
        print("\nDEBUG: Processing learning style analysis")
        result = await agent.process(state)

        # Ensure proper phase transition
        if "learning_style" not in result.get("completed_phases", []):
            result.setdefault("completed_phases", []).append("learning_style")

        # Force career_path as next phase from learning_style
        result["next"] = "career_path"
        result["current_phase"] = "career_path"

        return result
    except Exception as e:
        print(f"ERROR in process_learning: {str(e)}")
        traceback.print_exc()
        return {
            "message": "Error in learning style analysis",
            "next": "career_path",
            "current_phase": state.get("current_phase", "learning_style")
        }

async def process_career(state: Dict[str, Any], agent: CareerPathAnalyzer) -> Dict[str, Any]:
    """Process the career path analysis phase."""
    try:
        print("\nDEBUG: Processing career path analysis")
        result = await agent.process(state)

        # Ensure proper phase transition
        if "career_path" not in result.get("completed_phases", []):
            result.setdefault("completed_phases", []).append("career_path")

        # Force aggregate as next phase from career_path
        result["next"] = "aggregate"
        result["current_phase"] = "aggregate"

        return result
    except Exception as e:
        print(f"ERROR in process_career: {str(e)}")
        traceback.print_exc()
        return {
            "message": "Error in career path analysis",
            "next": "aggregate",
            "current_phase": state.get("current_phase", "career_path")
        }

async def process_aggregator(state: Dict[str, Any], agent: InsightAggregator) -> Dict[str, Any]:
    """Process the insight aggregation phase."""
    print("\nDEBUG: Processing insight aggregation")
    print(f"\nDEBUG: Processing insight aggregation - Current state: {state}")

    try:
        # Initialize result with current state
        result = state.copy()

        # Check if we have all required data
        has_learning_style = bool(result.get("learning_style", {}).get("primary_style"))
        has_career_path = bool(result.get("career_path", {}).get("suggested_path"))

        # Initialize completed phases if not present
        if "completed_phases" not in result:
            result["completed_phases"] = []

        # Process insights only if we haven't yet and have required data
        if "aggregate" not in result["completed_phases"] and has_learning_style and has_career_path:
            # Process insights with the agent
            agent_result = await agent.process(state)
            result.update(agent_result)

            # Add aggregate to completed phases
            result["completed_phases"].append("aggregate")

            # Ensure we don't duplicate messages
            if "messages" in result:
                result["messages"] = result["messages"][-5:]

        # Check if we have insights after processing
        has_insights = bool(result.get("collected_insights"))

        # Set next state based on completion
        if has_learning_style and has_career_path and has_insights and "aggregate" in result["completed_phases"]:
            result["next"] = END
            result["current_phase"] = "complete"
        else:
            result["next"] = "aggregate"
            result["current_phase"] = "aggregate"

        print(f"DEBUG: Aggregator result - next: {result.get('next')}, current_phase: {result.get('current_phase')}")
        print(f"DEBUG: Has insights: {has_insights}")
        print(f"DEBUG: Completed phases: {result.get('completed_phases')}")

        return result
    except Exception as e:
        print(f"ERROR in process_aggregator: {str(e)}")
        traceback.print_exc()
        return state

def create_interview_workflow(mock_responses: bool = False) -> StateGraph:
    """
    Create the interview workflow graph.

    Args:
        mock_responses (bool): Whether to use mock responses for testing.

    Returns:
        StateGraph: The compiled workflow graph.
    """
    try:
        # Initialize agents
        coordinator = InterviewCoordinator(mock_responses=mock_responses)
        learning_analyzer = LearningStyleAnalyzer(mock_responses=mock_responses)
        career_analyzer = CareerPathAnalyzer(mock_responses=mock_responses)
        insight_aggregator = InsightAggregator(mock_responses=mock_responses)
        print("DEBUG: Initialized all agents with mock responses")

        # Create workflow with proper state schema
        workflow = StateGraph(Annotated[InterviewState, "state"])
        print("DEBUG: Created StateGraph with typed state schema")

        # Create wrapper functions to handle agent process methods
        async def coordinator_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            # Initialize state if needed
            state.setdefault('current_phase', 'initial')
            state.setdefault('messages', [])
            state.setdefault('completed_phases', [])
            state.setdefault('collected_insights', {})
            state.setdefault('learning_style', {})
            state.setdefault('career_path', {})

            # Process coordinator phase
            result = await process_coordinator(state, coordinator)

            # Update phase completion
            if result.get("next") != "coordinator":
                result.setdefault("completed_phases", []).append("initial")

            return result

        async def learning_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            state["current_phase"] = "learning_style"
            result = await process_learning(state, learning_analyzer)

            # Update phase completion
            if result.get("next") != "learning_style":
                result.setdefault("completed_phases", []).append("learning_style")

            return result

        async def career_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            state["current_phase"] = "career_path"
            result = await process_career(state, career_analyzer)

            # Update phase completion
            if result.get("next") != "career_path":
                result.setdefault("completed_phases", []).append("career_path")

            return result

        async def aggregator_wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            state["current_phase"] = "aggregate"
            result = await process_aggregator(state, insight_aggregator)

            # Update phase completion
            if "aggregate" not in result.get("completed_phases", []):
                result.setdefault("completed_phases", []).append("aggregate")

            return result

        # Add nodes with wrapped process methods
        workflow.add_node("coordinator", coordinator_wrapper)
        workflow.add_node("learning_style", learning_wrapper)
        workflow.add_node("career_path", career_wrapper)
        workflow.add_node("aggregate", aggregator_wrapper)
        print("DEBUG: Added all workflow nodes")

        # Define conditional edges with strict phase progression
        workflow.add_conditional_edges(
            "coordinator",
            lambda x: END if should_end_interview(x) else (
                x.get("next", "learning_style") if x.get("next") == "learning_style"
                else "learning_style"
            ),
            {
                "learning_style": "learning_style",
                END: END
            }
        )

        workflow.add_conditional_edges(
            "learning_style",
            lambda x: END if should_end_interview(x) else (
                x.get("next", "career_path") if x.get("next") == "career_path"
                else "career_path"
            ),
            {
                "career_path": "career_path",
                END: END
            }
        )

        workflow.add_conditional_edges(
            "career_path",
            lambda x: END if should_end_interview(x) else (
                x.get("next", "aggregate") if x.get("next") == "aggregate"
                else "aggregate"
            ),
            {
                "aggregate": "aggregate",
                END: END
            }
        )

        workflow.add_conditional_edges(
            "aggregate",
            lambda x: END if (
                should_end_interview(x) or
                x.get("next") == END or
                (x.get("current_phase") == "complete" and
                 bool(x.get("collected_insights")))
            ) else "aggregate",
            {
                "aggregate": "aggregate",  # Add missing edge for self-transition
                END: END
            }
        )

        print("DEBUG: Added all conditional edges")

        # Set entry point
        workflow.set_entry_point("coordinator")
        print("DEBUG: Set entry point to coordinator")

        # Compile workflow before returning
        compiled_workflow = workflow.compile()
        print("DEBUG: Compiled workflow successfully")
        return compiled_workflow

    except Exception as e:
        print(f"ERROR in create_interview_workflow: {str(e)}")
        traceback.print_exc()
        return None
