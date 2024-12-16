"""Test cases for workflow functionality."""
import pytest
from typing import Dict, Any, cast
from langgraph.graph import END
from src.workflow import (
    InterviewState,
    create_interview_workflow
)

@pytest.mark.asyncio
async def test_workflow_creation():
    """Test workflow initialization."""
    workflow = create_interview_workflow(mock_responses=True)
    assert workflow is not None

@pytest.mark.asyncio
async def test_workflow_coordinator_phase():
    """Test coordinator phase processing."""
    workflow = create_interview_workflow(mock_responses=True)
    initial_state: InterviewState = {
        "current_phase": "initial",
        "messages": [],
        "completed_phases": [],
        "collected_insights": {},
        "learning_style": {},
        "career_path": {},
        "next": "coordinator"
    }

    result = await workflow.ainvoke(initial_state)
    assert isinstance(result, dict)
    assert "next" in result
    assert result["next"] == "learning_style"
    assert "completed_phases" in result
    assert "initial" in result["completed_phases"]

@pytest.mark.asyncio
async def test_workflow_learning_phase():
    """Test learning analyzer phase processing."""
    workflow = create_interview_workflow(mock_responses=True)
    state: InterviewState = {
        "current_phase": "learning_style",
        "messages": [],
        "completed_phases": ["initial"],
        "collected_insights": {"style_preference": "visual"},
        "learning_style": {},
        "career_path": {},
        "next": "learning_style"
    }

    result = await workflow.ainvoke(state)
    assert isinstance(result, dict)
    assert "next" in result
    assert result["next"] == "career_path"
    assert "completed_phases" in result
    assert "learning_style" in result["completed_phases"]
    assert "learning_style" in result
    assert result["learning_style"].get("primary_style") is not None

@pytest.mark.asyncio
async def test_workflow_career_phase():
    """Test career analyzer phase processing."""
    workflow = create_interview_workflow(mock_responses=True)
    state: InterviewState = {
        "current_phase": "career_path",
        "messages": [],
        "completed_phases": ["initial", "learning_style"],
        "collected_insights": {"career_goal": "developer"},
        "learning_style": {"primary_style": "visual"},
        "career_path": {},
        "next": "career_path"
    }

    result = await workflow.ainvoke(state)
    assert isinstance(result, dict)
    assert "next" in result
    assert result["next"] == "aggregate"
    assert "completed_phases" in result
    assert "career_path" in result["completed_phases"]
    assert "career_path" in result
    assert result["career_path"].get("suggested_path") is not None

@pytest.mark.asyncio
async def test_workflow_end_state():
    """Test workflow end state handling."""
    workflow = create_interview_workflow(mock_responses=True)
    state: InterviewState = {
        "current_phase": "aggregate",
        "messages": [],
        "completed_phases": ["initial", "learning_style", "career_path"],
        "collected_insights": {"complete": True},
        "learning_style": {"primary_style": "visual"},
        "career_path": {"suggested_path": "Full-stack Development"},
        "next": "aggregate"
    }

    result = await workflow.ainvoke(state)
    assert isinstance(result, dict)
    assert "next" in result
    assert result["next"] == END
    assert "completed_phases" in result
    assert "aggregate" in result["completed_phases"]
    assert "collected_insights" in result
    assert result["collected_insights"].get("complete") is True
