from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
import uuid
import traceback
from langgraph.graph import END

from .workflow import create_interview_workflow, InterviewState

app = FastAPI(
    title="User Profiling System",
    description="Multi-agent system for personalized learning path recommendations",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

interview_sessions: Dict[str, tuple[InterviewState, Any]] = {}

class InterviewResponse(BaseModel):
    message: str
    session_id: str
    phase: str
    completed_phases: List[str]

class UserInput(BaseModel):
    message: str

def process_user_input(workflow: Any, user_input: str, state: InterviewState) -> tuple[str, InterviewState]:
    print(f"\nDEBUG: Processing user input in phase: {state.current_phase}")
    print(f"DEBUG: Current completed phases: {state.completed_phases}")
    print(f"DEBUG: Current insights: {state.collected_insights}")

    try:
        if user_input:
            state.add_message({"role": "user", "content": user_input})

        # Create a copy of the state for workflow
        state_dict = state.dict()
        print(f"DEBUG: State dict before workflow: {state_dict}")

        # Invoke workflow and get result
        try:
            result = workflow.invoke(state_dict)
            print(f"DEBUG: Workflow result: {result}")
        except Exception as e:
            print(f"ERROR in workflow.invoke: {str(e)}")
            traceback.print_exc()
            return "I apologize, but I encountered an error in the workflow. Could you please try again?", state

        if result == END:
            print("DEBUG: Workflow reached END state")
            state.current_phase = "complete"
            return "Thank you for completing the interview! I'll prepare your personalized report.", state

        # Update existing state with new values
        if isinstance(result, dict):
            try:
                state.update_from_dict(result)
                print(f"DEBUG: State updated successfully - Phase: {state.current_phase}")
            except Exception as e:
                print(f"ERROR updating state: {str(e)}")
                traceback.print_exc()
                return "I apologize, but I encountered an error updating the interview state. Could you please try again?", state
        else:
            print(f"ERROR: Unexpected workflow result type: {type(result)}")
            return "I apologize, but I received an unexpected response. Could you please try again?", state

        last_message = state.get_last_message()
        if not last_message or "content" not in last_message:
            print("ERROR: No valid last message found")
            return "I apologize, but I couldn't process your response properly. Could you please try again?", state

        response = last_message["content"]
        print(f"DEBUG: Updated state - Phase: {state.current_phase}, Completed: {state.completed_phases}")
        return response, state

    except Exception as e:
        print(f"ERROR in process_user_input: {str(e)}")
        traceback.print_exc()
        return "I apologize, but I encountered an error processing your response. Could you please try again?", state

@app.post("/interview/start")
async def start_interview() -> InterviewResponse:
    """Start a new interview session."""
    try:
        session_id = str(uuid.uuid4())
        print(f"\nDEBUG: Starting new interview session: {session_id}")

        try:
            workflow = create_interview_workflow(mock_responses=True)
            print("DEBUG: Created workflow with mock responses")
        except Exception as e:
            print(f"ERROR creating workflow: {str(e)}")
            traceback.print_exc()
            raise ValueError(f"Failed to create workflow: {str(e)}")

        state = InterviewState()
        print(f"DEBUG: Initialized state - Phase: {state.current_phase}")

        # Initialize state with empty message to trigger first response
        try:
            response, updated_state = process_user_input(
                workflow=workflow,
                user_input="",
                state=state
            )
        except Exception as e:
            print(f"ERROR processing initial input: {str(e)}")
            traceback.print_exc()
            raise ValueError(f"Failed to process initial input: {str(e)}")

        if not response or not updated_state:
            raise ValueError("Failed to initialize interview state")

        interview_sessions[session_id] = (updated_state, workflow)

        return InterviewResponse(
            message=response,
            session_id=session_id,
            phase=updated_state.current_phase,
            completed_phases=updated_state.completed_phases
        )

    except Exception as e:
        print(f"ERROR in start_interview: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to start interview", "message": str(e)}
        )

@app.post("/interview/{session_id}/respond")
async def respond_to_interview(session_id: str, user_input: UserInput) -> InterviewResponse:
    """Process user response in interview session."""
    try:
        if session_id not in interview_sessions:
            raise HTTPException(
                status_code=404,
                detail={"error": "Session not found", "message": "Interview session not found"}
            )

        state, workflow = interview_sessions[session_id]
        print(f"\nDEBUG: Processing response for session {session_id}")
        print(f"DEBUG: Current state - Phase: {state.current_phase}")
        print(f"DEBUG: Current insights: {state.collected_insights}")

        try:
            response, updated_state = process_user_input(
                workflow=workflow,
                user_input=user_input.message,
                state=state
            )
        except Exception as e:
            print(f"ERROR processing user input: {str(e)}")
            traceback.print_exc()
            raise ValueError(f"Failed to process user input: {str(e)}")

        if not response or not updated_state:
            raise ValueError("Failed to process user input: no response or state update")

        # Update session state
        interview_sessions[session_id] = (updated_state, workflow)

        # Check if interview is complete
        if updated_state.current_phase == "complete":
            print("DEBUG: Interview complete, generating final response")
            return InterviewResponse(
                message="Thank you for completing the interview! I'll prepare your personalized report.",
                session_id=session_id,
                phase="complete",
                completed_phases=updated_state.completed_phases
            )

        return InterviewResponse(
            message=response,
            session_id=session_id,
            phase=updated_state.current_phase,
            completed_phases=updated_state.completed_phases
        )

    except ValueError as e:
        print(f"ERROR in respond_to_interview (ValueError): {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid request", "message": str(e)}
        )
    except Exception as e:
        print(f"ERROR in respond_to_interview: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to process response", "message": str(e)}
        )

@app.get("/interview/{session_id}/report")
async def get_interview_report(session_id: str):
    if session_id not in interview_sessions:
        raise HTTPException(status_code=404, detail="Interview session not found")

    state, _ = interview_sessions[session_id]
    if state.current_phase != "complete":
        raise HTTPException(
            status_code=400,
            detail="Interview is not complete. Final report not available."
        )

    return state.collected_insights.get("final_report", {})

@app.get("/")
async def root():
    return {"message": "User Profiling System API"}
