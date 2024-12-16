from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any
import uuid

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

        # Invoke workflow and get result
        result = workflow.invoke({
            "messages": state.messages,
            "current_phase": state.current_phase,
            "completed_phases": state.completed_phases,
            "collected_insights": state.collected_insights
        })

        print(f"DEBUG: Workflow result: {result}")

        # Create a new state instance with updated values
        new_state = InterviewState()
        new_state.messages = result.get("messages", state.messages)
        new_state.current_phase = result.get("current_phase", state.current_phase)
        new_state.completed_phases = result.get("completed_phases", state.completed_phases)
        new_state.collected_insights = result.get("collected_insights", state.collected_insights)

        last_message = new_state.get_last_message()
        response = last_message["content"] if last_message else "I apologize, but I couldn't process your response properly. Could you please try again?"

        print(f"DEBUG: Updated state - Phase: {new_state.current_phase}, Completed: {new_state.completed_phases}")
        return response, new_state

    except Exception as e:
        print(f"ERROR in process_user_input: {str(e)}")
        return "I apologize, but I encountered an error processing your response. Could you please rephrase or provide more details?", state

@app.post("/interview/start")
async def start_interview() -> InterviewResponse:
    try:
        session_id = str(uuid.uuid4())
        print(f"\nDEBUG: Starting new interview session: {session_id}")

        workflow = create_interview_workflow(mock_responses=True)
        print("DEBUG: Created workflow with mock responses")

        state = InterviewState()
        print(f"DEBUG: Initialized state - Phase: {state.current_phase}")

        response, updated_state = process_user_input(
            workflow=workflow,
            user_input="",
            state=state
        )

        interview_sessions[session_id] = (updated_state, workflow)

        return InterviewResponse(
            message=response,
            session_id=session_id,
            phase=updated_state.current_phase,
            completed_phases=updated_state.completed_phases
        )

    except Exception as e:
        print(f"ERROR in start_interview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to start interview", "message": str(e)}
        )

@app.post("/interview/{session_id}/respond")
async def respond_to_interview(
    session_id: str,
    user_input: UserInput
) -> InterviewResponse:
    try:
        if session_id not in interview_sessions:
            raise HTTPException(
                status_code=404,
                detail="Interview session not found"
            )

        state, workflow = interview_sessions[session_id]
        print(f"\nDEBUG: Processing response for session {session_id}")
        print(f"DEBUG: Current phase: {state.current_phase}")
        print(f"DEBUG: Completed phases: {state.completed_phases}")

        response, new_state = process_user_input(
            workflow=workflow,
            user_input=user_input.message,
            state=state
        )

        interview_sessions[session_id] = (new_state, workflow)

        return InterviewResponse(
            message=response,
            session_id=session_id,
            phase=new_state.current_phase,
            completed_phases=new_state.completed_phases
        )

    except Exception as e:
        print(f"ERROR in respond_to_interview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to process interview response", "message": str(e)}
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
