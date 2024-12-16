from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uuid
import traceback
from langgraph.graph import END

from src.workflow import create_interview_workflow

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

interview_sessions: Dict[str, Any] = {}

class InterviewResponse(BaseModel):
    message: str
    session_id: str
    phase: str
    completed_phases: List[str]

class UserInput(BaseModel):
    message: str

async def process_user_input(workflow: Any, user_input: str, state: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    print(f"\nDEBUG: Processing user input - State: {state}")

    try:
        if user_input:
            if "messages" not in state:
                state["messages"] = []
            state["messages"].append({"role": "user", "content": user_input})

        # Invoke workflow with current state
        try:
            print("DEBUG: Invoking workflow with state")
            result = await workflow.ainvoke(state)  # Changed from arun to ainvoke
            print(f"DEBUG: Workflow result: {result}")

            # Handle END state
            if result == END:
                print("DEBUG: Workflow reached END state")
                state["current_phase"] = "complete"
                if "completed_phases" not in state:
                    state["completed_phases"] = []
                state["completed_phases"].append("complete")
                return "Thank you for completing the interview! I'll prepare your personalized report.", state

            # Update state from workflow result
            if isinstance(result, dict):
                try:
                    print("DEBUG: Updating state with workflow result")
                    # Preserve existing state and merge with workflow result
                    for key, value in result.items():
                        if key == "messages" and "messages" in state:
                            state["messages"].extend([msg for msg in value if msg not in state["messages"]])
                        elif key == "completed_phases" and "completed_phases" in state:
                            state["completed_phases"] = list(dict.fromkeys(state["completed_phases"] + value))
                        else:
                            state[key] = value

                    state.setdefault("current_phase", "initial")
                    state.setdefault("completed_phases", [])
                    state.setdefault("messages", [])
                    state.setdefault("learning_style", {})
                    state.setdefault("career_path", {})
                    state.setdefault("insights", [])

                    print(f"DEBUG: Updated state - Phase: {state.get('current_phase')}")
                    print(f"DEBUG: Completed phases: {state.get('completed_phases', [])}")
                    print(f"DEBUG: Learning style: {state.get('learning_style', {})}")
                    print(f"DEBUG: Career path: {state.get('career_path', {})}")
                    print(f"DEBUG: Insights: {state.get('insights', [])}")
                except Exception as e:
                    print(f"ERROR updating state: {str(e)}")
                    traceback.print_exc()
                    return "I apologize, but I encountered an error updating the interview state.", state
            else:
                print(f"ERROR: Unexpected workflow result type: {type(result)}")
                return "I apologize, but I received an unexpected response.", state

            messages = state.get("messages", [])
            if not messages:
                return state.get("message", "I apologize, but I couldn't process your response properly."), state

            last_message = messages[-1]
            response = last_message["content"] if isinstance(last_message, dict) else str(last_message)
            return response, state

        except Exception as e:
            print(f"ERROR in workflow.ainvoke: {str(e)}")  # Updated error message
            traceback.print_exc()
            return "I apologize, but I encountered an error in the workflow.", state

    except Exception as e:
        print(f"ERROR in process_user_input: {str(e)}")
        traceback.print_exc()
        return "I apologize, but I encountered an error processing your response.", state

@app.post("/interview/start", response_model=InterviewResponse)
async def start_interview():
    """Start a new interview session."""
    try:
        session_id = str(uuid.uuid4())
        print(f"\nDEBUG: Starting new interview session: {session_id}")

        # Create workflow with mock responses
        workflow = create_interview_workflow(mock_responses=True)
        print("DEBUG: Created workflow with mock responses enabled")

        if not workflow:
            raise HTTPException(status_code=500, detail="Failed to create interview workflow")

        # Initialize state
        state = {
            "next": "learning_style",
            "current_phase": "initial",
            "message": "Hello! I'll be conducting your interview today. To start, could you tell me about your recent learning experiences?",
            "messages": [{"role": "assistant", "content": "Hello! I'll be conducting your interview today. To start, could you tell me about your recent learning experiences?"}],
            "user_responses": {},
            "learning_style": {},
            "career_path": {},
            "insights": [],
            "report": None,
            "completed_phases": [],
            "session_id": session_id
        }
        print("DEBUG: Initialized state - Phase: initial")

        # Store workflow and state
        interview_sessions[session_id] = (workflow, state)

        # Process initial message
        response, updated_state = await process_user_input(workflow, "", state)
        print(f"DEBUG: Initial workflow response: {response}")
        print(f"DEBUG: Initial state update: {updated_state}")

        return InterviewResponse(
            message=response,
            session_id=session_id,
            phase=updated_state.get("current_phase", "initial"),
            completed_phases=updated_state.get("completed_phases", [])
        )

    except Exception as e:
        print(f"ERROR in start_interview: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interview/{session_id}/respond", response_model=InterviewResponse)
async def respond_to_interview(session_id: str, user_input: UserInput):
    """Process user input and continue the interview."""
    try:
        print(f"\nDEBUG: Processing response for session {session_id}")

        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="Interview session not found")

        workflow, state = interview_sessions[session_id]
        print(f"DEBUG: Current state - Phase: {state.get('current_phase', 'unknown')}")

        # Process user input
        response, updated_state = await process_user_input(workflow, user_input.message, state)

        # Update session state
        interview_sessions[session_id] = (workflow, updated_state)

        return InterviewResponse(
            message=response,
            session_id=session_id,
            phase=updated_state.get("current_phase", "initial"),
            completed_phases=updated_state.get("completed_phases", [])
        )

    except Exception as e:
        print(f"ERROR in respond_to_interview: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interview/{session_id}/report")
async def get_interview_report(session_id: str):
    """Get the final interview report."""
    try:
        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="Interview session not found")

        _, state = interview_sessions[session_id]
        if "report" not in state or not state["report"]:
            raise HTTPException(status_code=400, detail="Report not yet available")

        return {"report": state["report"]}

    except Exception as e:
        print(f"ERROR in get_interview_report: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"status": "running"}
