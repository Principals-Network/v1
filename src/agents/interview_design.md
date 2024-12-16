# Interactive Interview System Design

## System Architecture

### 1. Agent Roles

1. **Interview Coordinator Agent**
   - Manages the overall flow of the interview
   - Coordinates between specialized agents
   - Ensures smooth transitions between topics
   - Maintains conversation context

2. **Learning Style Analyzer Agent**
   - Focuses on identifying preferred learning methods
   - Analyzes responses for learning style indicators
   - Categories: Visual, Auditory, Kinesthetic, Reading/Writing
   - Identifies optimal content delivery methods

3. **Career Path Analyzer Agent**
   - Explores professional interests and goals
   - Analyzes skill gaps and development needs
   - Maps career trajectory possibilities
   - Identifies industry-specific requirements

4. **Insight Aggregator Agent**
   - Collects and synthesizes information from other agents
   - Maintains long-term memory of user insights
   - Generates comprehensive user profiles
   - Prepares data for learning path generation

## Interview Flow

### Phase 1: Initial Assessment
1. Background Information
   - Educational history
   - Professional experience
   - Current role and responsibilities
   - Time availability for learning

2. Learning Style Assessment
   - Past learning experiences
   - Preferred content formats
   - Study environment preferences
   - Time management patterns

### Phase 2: Career Exploration
1. Professional Goals
   - Short-term objectives (1-2 years)
   - Long-term aspirations (3-5 years)
   - Industry interests
   - Role preferences

2. Skills Assessment
   - Current technical skills
   - Soft skills inventory
   - Desired skill acquisitions
   - Priority areas for development

### Phase 3: Learning Preferences
1. Content Delivery
   - Format preferences (video, text, interactive)
   - Optimal session duration
   - Preferred learning schedule
   - Group vs. individual learning

2. Engagement Style
   - Interactive vs. passive learning
   - Project-based vs. theoretical learning
   - Assessment preferences
   - Feedback style preferences

## Data Collection Framework

### 1. User Profile Schema
```json
{
  "personal_info": {
    "background": "string",
    "current_role": "string",
    "time_availability": "string"
  },
  "learning_style": {
    "primary_style": "string",
    "secondary_style": "string",
    "environment_preferences": ["string"],
    "content_preferences": ["string"]
  },
  "career_goals": {
    "short_term": ["string"],
    "long_term": ["string"],
    "target_industries": ["string"],
    "target_roles": ["string"]
  },
  "skills": {
    "technical": ["string"],
    "soft": ["string"],
    "development_areas": ["string"],
    "priorities": ["string"]
  },
  "learning_preferences": {
    "content_format": ["string"],
    "session_duration": "string",
    "schedule_preference": "string",
    "engagement_style": "string"
  }
}
```

### 2. Interview Strategy
- Use open-ended questions to gather detailed insights
- Implement follow-up questions based on initial responses
- Maintain conversation context for personalized follow-ups
- Use semantic search for relevant past information
- Store insights in vector database for future reference

## Implementation Notes

### State Management
- Use LangGraph's state management to track interview progress
- Maintain conversation history for context
- Store intermediate insights from each agent
- Track completion status of each interview phase

### Agent Communication
- Implement message passing between agents
- Use shared memory for collaborative insight generation
- Maintain agent-specific context states
- Coordinate parallel processing of user responses

### Memory System
- Implement short-term memory for immediate context
- Use long-term memory for persistent user insights
- Implement semantic search for relevant information retrieval
- Store structured data for academy customization

### Output Generation
- Create detailed user profile report
- Generate learning style analysis
- Provide career path recommendations
- Outline customized academy structure recommendations
