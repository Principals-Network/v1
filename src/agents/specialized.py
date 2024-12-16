"""Specialized agents for the user profiling system."""

from typing import Dict, List, Any, Optional
import traceback
from pydantic import BaseModel
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END
from .base import BaseAgent, AgentState

class InterviewState(AgentState):
    """Extended state for interview coordination."""
    phase_questions: Dict[str, str] = {}
    current_question: Optional[str] = None
    phase_completion: Dict[str, bool] = {
        "initial": False,
        "learning_style": False,
        "career_goals": False,
        "skills_assessment": False
    }

class LearningStyleState(AgentState):
    """Extended state for learning style analysis."""
    analysis_complete: bool = False
    learning_style: Dict[str, Any] = {}
    recommendations: List[str] = []

class CareerPathState(AgentState):
    """Extended state for career path analysis."""
    career_path: Dict[str, Any] = {}
    roadmap: List[Dict[str, Any]] = []
    skill_gaps: List[str] = []

class AggregatorState(AgentState):
    """Extended state for insight aggregation."""
    aggregation_complete: bool = False
    report: Optional[Dict[str, Any]] = None

class InterviewCoordinatorAgent(BaseAgent):
    """Manages the overall flow of the interview process."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Interview Coordinator",
            system_prompt="""You are an expert learning and career development advisor.
            Guide the conversation through different phases to understand the user's learning style,
            career goals, and current skills for personalized recommendations.""",
            state=InterviewState(),
            mock_responses=mock_responses
        )
        self.mock_responses = {
            "initial": "I understand. Let's start by understanding your learning style. Could you tell me about how you prefer to learn new things?",
            "learning_style": "I see. Now, let's discuss your career goals. What kind of role or industry interests you?",
            "career_goals": "Great insights about your career interests. Let's assess your current skills. What technical or soft skills do you already have?",
            "skills_assessment": "Thank you for sharing. I'll analyze this information to create your personalized learning path."
        } if mock_responses else {}

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and determine next steps."""
        try:
            print(f"\nDEBUG: Processing interview - Current state: {state}")

            # Initialize state if needed
            if not state.get('current_phase'):
                state['current_phase'] = 'initial'
            if 'messages' not in state:
                state['messages'] = []
            if 'completed_phases' not in state:
                state['completed_phases'] = []
            if 'collected_insights' not in state:
                state['collected_insights'] = {}

            current_phase = state.get('current_phase', 'initial')
            completed_phases = state.get('completed_phases', [])

            # Generate response based on current state
            if self.mock_responses:
                # Phase-specific responses with consistent state management
                phase_responses = {
                    "initial": {
                        "next": "learning_style",
                        "current_phase": "learning_style",
                        "message": "Hello! I'll be conducting your interview today. To start, could you tell me about how you prefer to learn new things?",
                        "completed_phases": completed_phases + ["initial"] if "initial" not in completed_phases else completed_phases,
                        "messages": state.get("messages", []) + [{"role": "assistant", "content": "Hello! I'll be conducting your interview today. To start, could you tell me about how you prefer to learn new things?"}]
                    },
                    "learning_style": {
                        "next": "career_path",
                        "current_phase": "career_path",
                        "message": "Thank you for sharing your learning preferences. Now, let's discuss your career goals. What kind of role or industry interests you?",
                        "completed_phases": completed_phases + ["learning_style"] if "learning_style" not in completed_phases else completed_phases,
                        "messages": state.get("messages", []) + [{"role": "assistant", "content": "Thank you for sharing your learning preferences. Now, let's discuss your career goals. What kind of role or industry interests you?"}],
                        "learning_style": {"preferred_methods": ["hands-on", "project-based"], "strengths": ["practical application", "experimentation"]}
                    },
                    "career_path": {
                        "next": "aggregate",
                        "current_phase": "aggregate",
                        "message": "I understand your career interests. Let's analyze all the information you've shared to create your personalized learning path.",
                        "completed_phases": completed_phases + ["career_path"] if "career_path" not in completed_phases else completed_phases,
                        "messages": state.get("messages", []) + [{"role": "assistant", "content": "I understand your career interests. Let's analyze all the information you've shared to create your personalized learning path."}],
                        "career_path": {"goals": ["software development"], "interests": ["backend", "distributed systems"]}
                    }
                }

                # Get response for current phase
                result = phase_responses.get(current_phase, phase_responses["initial"])
                print(f"DEBUG: Generated mock response for phase {current_phase}: {result}")
                return result
            else:
                result = await self._generate_real_response(state)
                return result

        except Exception as e:
            print(f"ERROR in process: {str(e)}")
            traceback.print_exc()
            return self._error_response(state)

    def _error_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate error response with safe fallback."""
        return {
            "message": "I apologize, but I encountered an error processing your response.",
            "next": state.get("next", "learning_style"),
            "current_phase": state.get("current_phase", "initial"),
            "completed_phases": state.get("completed_phases", [])
        }

class LearningStyleAnalyzerAgent(BaseAgent):
    """Analyzes user responses to determine optimal learning style."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Learning Style Analyzer",
            system_prompt="""You are an expert in learning style analysis.
            Analyze user responses to determine their optimal learning approach.""",
            state=LearningStyleState(),
            mock_responses=mock_responses
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state to analyze learning style."""
        try:
            print(f"\nDEBUG: Processing learning style analysis - Current state: {state}")

            if self.mock_responses:
                result = self._generate_mock_analysis(state)
            else:
                result = await self._generate_real_analysis(state)

            # Update state with learning style analysis
            state.update(result)
            state['next'] = 'career_path'
            state['current_phase'] = 'career_path'
            if 'learning_style' not in state.get('completed_phases', []):
                state.setdefault('completed_phases', []).append('learning_style')

            return state

        except Exception as e:
            print(f"ERROR in process: {str(e)}")
            traceback.print_exc()
            return self._error_response(state)

    def _generate_mock_analysis(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock learning style analysis."""
        return {
            "messages": state.get('messages', []) + [{
                "role": "assistant",
                "content": "Based on our analysis, your learning style appears to be primarily visual-kinesthetic."
            }],
            "learning_style": {
                "primary_style": "visual-kinesthetic",
                "strengths": ["Visual learning", "Hands-on practice"],
                "recommendations": ["Use diagrams", "Interactive exercises"],
                "confidence": 0.85
            }
        }

    def _error_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate error response with safe fallback."""
        return {
            "messages": state.get('messages', []) + [{
                "role": "assistant",
                "content": "I apologize, but I encountered an error analyzing your learning style. Could you please try again?"
            }],
            "next": "learning_style",
            "current_phase": "learning_style"
        }

class CareerPathAnalyzerAgent(BaseAgent):
    """Analyzes user goals and background to suggest career paths."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Career Path Analyzer",
            system_prompt="""You are an expert in career development and planning.
            Analyze user goals and background to create personalized career roadmaps.""",
            state=CareerPathState(),
            mock_responses=mock_responses
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state to analyze career path."""
        try:
            print(f"\nDEBUG: Processing career path analysis - Current state: {state}")

            if self.mock_responses:
                result = self._generate_mock_roadmap(state)
            else:
                result = await self._generate_real_roadmap(state)

            # Update state with career path analysis
            state.update(result)
            state['next'] = 'aggregate'
            state['current_phase'] = 'aggregate'
            if 'career_path' not in state.get('completed_phases', []):
                state.setdefault('completed_phases', []).append('career_path')

            return state

        except Exception as e:
            print(f"ERROR in process: {str(e)}")
            traceback.print_exc()
            return self._error_response(state)

    def _generate_mock_roadmap(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock career path analysis."""
        return {
            "messages": state.get('messages', []) + [{
                "role": "assistant",
                "content": "Based on your goals and background, here's a suggested career development path."
            }],
            "career_path": {
                "suggested_path": "Full-stack Development",
                "milestones": ["Frontend basics", "Backend development", "DevOps"],
                "timeline": "12-18 months",
                "confidence": 0.9
            }
        }

    def _error_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate error response with safe fallback."""
        return {
            "messages": state.get('messages', []) + [{
                "role": "assistant",
                "content": "I apologize, but I encountered an error analyzing your career path. Could you please try again?"
            }],
            "next": "career_path",
            "current_phase": "career_path"
        }

class InsightAggregatorAgent(BaseAgent):
    """Aggregates insights from all analyses to generate final report."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Insight Aggregator",
            system_prompt="""You are an expert in synthesizing learning and career insights.
            Combine analyses to create comprehensive, actionable recommendations.""",
            state=AggregatorState(),
            mock_responses=mock_responses
        )

    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state to aggregate insights and generate report."""
        try:
            print(f"\nDEBUG: Processing insight aggregation - Current state: {state}")

            if self.mock_responses:
                result = self._format_insights(state)
            else:
                result = await self._generate_real_insights(state)

            # Update state with aggregated insights and final report
            state.update(result)
            state['next'] = END
            state['current_phase'] = 'complete'
            if 'aggregate' not in state['completed_phases']:
                state['completed_phases'].append('aggregate')

            return state

        except Exception as e:
            print(f"ERROR in process: {str(e)}")
            traceback.print_exc()
            return self._error_response(state)

    def _format_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Format collected insights for report generation."""
        learning_style = insights.get('learning_style', {})
        career_roadmap = insights.get('career_roadmap', {})

        return {
            "messages": insights.get('messages', []) + [{
                "role": "assistant",
                "content": "\n".join([
                    "Based on the collected insights, generate a comprehensive development report:",
                    "---",
                    "Learning Style Analysis:",
                    f"{learning_style.get('analysis', 'Not available')}",
                    "---",
                    "Career Roadmap:",
                    f"{career_roadmap.get('analysis', 'Not available')}",
                    "---",
                    "Please provide a detailed report including:",
                    "1. Learning profile and preferences",
                    "2. Career development pathway",
                    "3. Specific recommendations for:",
                    "   - Learning approaches",
                    "   - Skill development",
                    "   - Immediate next steps",
                    "4. Timeline and milestones",
                    "Format the response as a comprehensive yet conversational report."
                ])
            }],
            "current_phase": "complete",
            "collected_insights": {"final_report": {
                "analysis": "Mock analysis",
                "confidence": 0.9,
                "timestamp": "auto-generated"
            }},
            "next": END
        }

    def _error_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate error response with safe fallback."""
        return {
            "messages": state.get('messages', []) + [{
                "role": "assistant",
                "content": "I apologize, but I encountered an error generating your comprehensive report. Could you please try again?"
            }],
            "current_phase": "complete",
            "collected_insights": {},
            "next": END
        }
