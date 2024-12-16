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

        # Invoke workflow and get result
        result = workflow.invoke(state_dict)
        print(f"DEBUG: Workflow result: {result}")

        if result == END:
            print("DEBUG: Workflow reached END state")
            state.current_phase = "complete"
            return "Thank you for completing the interview! I'll prepare your personalized report.", state

        # Update existing state with new values
        try:
            state.update_from_dict(result)
            print(f"DEBUG: State updated successfully - Phase: {state.current_phase}")
        except Exception as e:
            print(f"ERROR updating state: {str(e)}")
            return "I apologize, but I encountered an error updating the interview state. Could you please try again?", state

        last_message = state.get_last_message()
        response = last_message.get("content") if last_message else "I apologize, but I couldn't process your response properly. Could you please try again?"

        print(f"DEBUG: Updated state - Phase: {state.current_phase}, Completed: {state.completed_phases}")
        return response, state

    except Exception as e:
        print(f"ERROR in process_user_input: {str(e)}")
        return "I apologize, but I encountered an error processing your response. Could you please rephrase or provide more details?", state

@app.post("/interview/start")
async def start_interview() -> InterviewResponse:
    """Start a new interview session."""
    try:
        session_id = str(uuid.uuid4())
        print(f"\nDEBUG: Starting new interview session: {session_id}")

        workflow = create_interview_workflow(mock_responses=True)
        print("DEBUG: Created workflow with mock responses")

        state = InterviewState()
        print(f"DEBUG: Initialized state - Phase: {state.current_phase}")

        # Initialize state with empty message to trigger first response
        response, updated_state = process_user_input(
            workflow=workflow,
            user_input="",
            state=state
        )

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
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/interview/{session_id}/respond")
async def respond_to_interview(session_id: str, user_input: UserInput) -> InterviewResponse:
    try:
        if session_id not in interview_sessions:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )

        state, workflow = interview_sessions[session_id]
        print(f"\nDEBUG: Processing response for session {session_id}")
        print(f"DEBUG: Current state - Phase: {state.current_phase}")
        print(f"DEBUG: Current insights: {state.collected_insights}")

        response, updated_state = process_user_input(
            workflow=workflow,
            user_input=user_input.message,
            state=state
        )

        if not response or not updated_state:
            raise ValueError("Failed to process user input")

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

    except Exception as e:
        print(f"ERROR in respond_to_interview: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
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
