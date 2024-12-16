# User Profiling System

A multi-agent system built with Langgraph for creating personalized learning experiences through interactive interviews.

## Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
- Copy `.env.example` to `.env`
- Add your OpenAI API key to `.env`

## Running the Application

```bash
uvicorn src.main:app --reload
```
