"""Specialized agents for the user profiling system."""

from typing import Dict, List, Any, Optional
import traceback
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END
from .base import BaseAgent, AgentState

class InterviewCoordinatorAgent(BaseAgent):
    """Manages the overall flow of the interview process."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Interview Coordinator",
            system_prompt="""You are an expert learning and career development advisor.
            Guide the conversation through different phases to understand the user's learning style,
            career goals, and current skills for personalized recommendations.""",
            mock_responses=mock_responses
        )
        self.state.set("current_phase", "initial")
        self.state.set("phase_completion", {
            "initial": False,
            "learning_style": False,
            "career_goals": False,
            "skills_assessment": False
        })
        self.mock_responses = {
            "initial": "Welcome! I'm excited to help create your personalized learning journey. To start, could you tell me about your recent learning experiences? What methods have worked well for you, and what challenges have you faced?",
            "learning_style": "Thank you for sharing. Based on what you've mentioned, I'd like to explore your learning preferences further. When learning something new, do you prefer practical exercises, theoretical understanding, visual aids, or discussion-based learning? Could you give specific examples?",
            "career_goals": "Now that I understand your learning style better, let's discuss your career aspirations. What roles or positions interest you most? Where do you see yourself in 3-5 years, and what skills do you think you'll need to get there?",
            "skills_assessment": "Great career goals! To help create your personalized learning path, could you tell me about your current technical skills and expertise? What areas do you feel confident in, and where would you like to improve?"
        }
        self.llm = None if mock_responses else ChatOpenAI(temperature=0.7)

    def determine_next_phase(self) -> str:
        """Determine the next interview phase based on current progress."""
        phase_completion = self.state.get("phase_completion", {})
        current_phase = self.state.get("current_phase")

        if not phase_completion.get(current_phase, False):
            return current_phase

        if not phase_completion.get("initial", False):
            return "initial"
        elif not phase_completion.get("learning_style", False):
            return "learning_style"
        elif not phase_completion.get("career_goals", False):
            return "career_goals"
        elif not phase_completion.get("skills_assessment", False):
            return "skills_assessment"
        return "complete"

    def generate_response(self, user_input: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            current_phase = self.state.get("current_phase")
            phase_completion = self.state.get("phase_completion", {})

            print(f"DEBUG: Generating response for phase: {current_phase}")
            print(f"DEBUG: Current phase completion status: {phase_completion}")
            print(f"DEBUG: Processing user input: {user_input[:100] if user_input else 'None'}...")

            # For initial empty state, return welcome message
            if not user_input and current_phase == "initial":
                return {
                    "messages": context + [{"role": "assistant", "content": self.mock_responses["initial"]}],
                    "current_phase": current_phase,
                    "collected_insights": {},
                    "next": "coordinator"
                }

            # Process user input and transition phases
            if user_input:
                try:
                    phase_transitions = {
                        "initial": ("learning_style", "learning_analyzer", "initial_insights"),
                        "learning_style": ("career_goals", "career_analyzer", "learning_style_insights"),
                        "career_goals": ("skills_assessment", "aggregator", "career_goals_insights"),
                        "skills_assessment": ("complete", END, "skills_assessment_insights")
                    }

                    if current_phase in phase_transitions:
                        next_phase, next_node, insight_key = phase_transitions[current_phase]

                        # Update phase completion and current phase
                        phase_completion[current_phase] = True
                        self.state.set("phase_completion", phase_completion)
                        self.state.set("current_phase", next_phase)

                        # Prepare response with collected insights
                        return {
                            "messages": context + [{"role": "assistant", "content": self.mock_responses.get(next_phase, "Thank you for sharing!")}],
                            "current_phase": next_phase,
                            "collected_insights": {insight_key: {"user_input": user_input}},
                            "next": next_node
                        }

                except Exception as e:
                    print(f"ERROR in phase transition: {str(e)}")
                    traceback.print_exc()

            # Default response for unknown states
            return {
                "messages": context + [{"role": "assistant", "content": self.mock_responses.get(current_phase, "I didn't catch that. Could you please try again?")}],
                "current_phase": current_phase,
                "collected_insights": {},
                "next": "coordinator"
            }

        except Exception as e:
            print(f"ERROR in generate_response: {str(e)}")
            traceback.print_exc()
            return {
                "messages": context + [{"role": "assistant", "content": "I apologize, but I encountered an error. Could you please try again?"}],
                "current_phase": self.state.get("current_phase", "initial"),
                "collected_insights": {},
                "next": "coordinator"
            }

class LearningStyleAnalyzerAgent(BaseAgent):
    """Analyzes user responses for learning style preferences."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Learning Style Analyzer",
            system_prompt="""You are an expert in learning styles and educational psychology.
            Analyze responses to identify preferred learning methods, strengths, and areas for improvement.""",
            mock_responses=mock_responses
        )
        self.mock_analysis = {
            "learning_style": "hands-on, practical",
            "preferred_methods": ["project-based", "interactive", "experiential"],
            "strengths": ["practical application", "experimental learning"],
            "areas_for_improvement": ["theoretical foundations"],
            "confidence": 0.8,
            "analysis": "User shows strong preference for hands-on, practical learning approaches. Kinesthetic learning style is dominant, with emphasis on project-based learning."
        }
        self.llm = None

    def analyze_response(self, user_input: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user response for learning style insights."""
        try:
            if self.mock_responses:
                analysis = {
                    "learning_style": "Visual and hands-on learner",
                    "preferred_methods": ["Project-based learning", "Interactive tutorials", "Visual documentation"],
                    "challenges": ["Traditional lectures", "Text-only materials"],
                    "recommendations": ["Focus on practical projects", "Use visual learning aids", "Interactive coding exercises"]
                }
                return {
                    "messages": context + [{
                        "role": "assistant",
                        "content": "Based on your responses, you show a strong preference for visual and hands-on learning approaches."
                    }],
                    "current_phase": "learning_style",
                    "collected_insights": {"learning_style": analysis},
                    "next": "coordinator"
                }
            else:
                # Implement actual LLM-based analysis here
                pass

        except Exception as e:
            print(f"ERROR in analyze_response: {str(e)}")
            return {
                "messages": context,
                "current_phase": "learning_style",
                "collected_insights": {},
                "next": "coordinator"
            }

class CareerPathAnalyzerAgent(BaseAgent):
    """Analyzes career goals and creates development roadmaps."""

    def __init__(self, mock_responses: bool = True):
        """Initialize career path analyzer."""
        super().__init__(
            name="Career Path Analyzer",
            system_prompt="""You are an expert career development advisor specializing in technology careers.
            Create personalized career development roadmaps based on goals, skills, and aspirations.""",
            mock_responses=mock_responses
        )
        self.mock_roadmap = {
            "career_path": "Software Architect",
            "milestones": [
                "Master system design principles",
                "Gain experience with distributed systems",
                "Develop leadership skills"
            ],
            "required_skills": {
                "technical": [
                    "System design patterns",
                    "Cloud architecture",
                    "Distributed systems"
                ],
                "soft_skills": [
                    "Technical leadership",
                    "Communication",
                    "Project management"
                ]
            },
            "learning_path": [
                "Complete system design courses",
                "Work on distributed system projects",
                "Lead technical initiatives"
            ],
            "confidence": 0.9
        }
        self.llm = None

    def create_roadmap(self, user_input: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create career development roadmap."""
        try:
            if self.mock_responses:
                roadmap = {
                    "career_path": "Software Architect",
                    "milestones": [
                        "Master system design principles",
                        "Gain experience with distributed systems",
                        "Develop leadership skills"
                    ],
                    "skills_needed": [
                        "Advanced system design",
                        "Cloud architecture",
                        "Technical leadership"
                    ]
                }
                return {
                    "messages": context + [{
                        "role": "assistant",
                        "content": "I've created a roadmap focused on your software architect career goals."
                    }],
                    "current_phase": "career_goals",
                    "collected_insights": {"career_goals": roadmap},
                    "next": "coordinator"
                }
            else:
                # Implement actual LLM-based roadmap creation here
                pass

        except Exception as e:
            print(f"ERROR in create_roadmap: {str(e)}")
            return {
                "messages": context,
                "current_phase": "career_goals",
                "collected_insights": {},
                "next": "coordinator"
            }

class InsightAggregatorAgent(BaseAgent):
    """Aggregates insights from all phases to generate comprehensive reports."""

    def __init__(self, mock_responses: bool = True):
        super().__init__(
            name="Insight Aggregator",
            system_prompt="""You are an expert in synthesizing educational and career development insights.
            Create comprehensive personal development recommendations based on learning style, career goals, and skills.""",
            mock_responses=mock_responses
        )
        self.mock_report = {
            "learning_profile": {
                "primary_style": "Hands-on, practical learner",
                "effective_methods": [
                    "Project-based learning",
                    "Interactive workshops",
                    "Practical exercises"
                ]
            },
            "career_development": {
                "target_role": "Technical Architect",
                "key_milestones": [
                    "Complete system design certification",
                    "Lead team projects",
                    "Contribute to architecture decisions"
                ]
            },
            "recommendations": [
                "Focus on hands-on architectural exercises",
                "Join technical leadership workshops",
                "Participate in team projects to develop leadership skills"
            ]
        }
        self.llm = None

    def generate_report(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final insights report."""
        try:
            if self.mock_responses:
                report = {
                    "learning_profile": insights.get("learning_style", {}),
                    "career_development": insights.get("career_goals", {}),
                    "recommendations": {
                        "learning_approach": "Project-based curriculum with visual aids",
                        "skill_development": "Focus on system design and cloud architecture",
                        "next_steps": "Begin with hands-on distributed systems projects"
                    }
                }
                return {
                    "messages": [{"role": "assistant", "content": "Your personalized learning and career development report is ready."}],
                    "current_phase": "complete",
                    "collected_insights": {"final_report": report},
                    "next": "END"
                }
            else:
                # Implement actual LLM-based report generation here
                pass

        except Exception as e:
            print(f"ERROR in generate_report: {str(e)}")
            return {
                "messages": [],
                "current_phase": "complete",
                "collected_insights": {},
                "next": "coordinator"
            }
