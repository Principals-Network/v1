#!/bin/bash

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Function to send request and handle response
send_request() {
    local phase=$1
    local message=$2
    echo "Sending $phase response..."
    RESPONSE=$(curl -s -X POST "http://localhost:8001/interview/$SESSION_ID/respond" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d "{\"message\": \"$message\"}")
    echo "$RESPONSE" | python3 -m json.tool
    echo -e "\nWaiting for 2 seconds..."
    sleep 2
}

# Start new interview session and capture the session ID
echo "Starting new interview session..."
RESPONSE=$(curl -s -X POST http://localhost:8001/interview/start \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{}')

SESSION_ID=$(echo "$RESPONSE" | python3 scripts/parse_session.py)

if [ -z "$SESSION_ID" ]; then
    handle_error "Failed to get session ID from response: $RESPONSE"
fi

echo "Started interview session: $SESSION_ID"

# Initial phase response
send_request "initial" "I'm a software developer with 5 years of experience, primarily focused on backend development. I've found that I learn best through hands-on projects and practical applications. Traditional lectures or passive learning methods don't work well for me - I need to actively build things to understand concepts deeply. I'm particularly interested in improving my system design skills and learning more about distributed systems and cloud architecture. When I encounter new technologies, I prefer to start with small prototype projects where I can experiment with the code and see how things work in practice."

# Learning style phase response
send_request "learning style" "When learning new programming concepts, I find project-based learning and hands-on implementation most effective. I learn best by understanding the underlying principles through practical experience. For debugging, I prefer systematic approaches where I can experiment with different solutions and learn from the outcomes. Documentation is important, but I need to combine it with actual coding practice to fully grasp concepts."

# Career goals phase response
send_request "career goals" "My career goals include becoming a senior software architect in the next few years. I'm particularly interested in distributed systems and cloud architecture. I want to lead technical decisions and mentor other developers. In the future, I see myself designing large-scale systems and contributing to open-source projects in the cloud-native space."

# Skills assessment phase response
send_request "skills assessment" "I'm confident in my skills with Python, Go, and backend development patterns. I have strong experience with microservices and API design. Areas I want to improve include system design for large-scale applications, advanced cloud architecture patterns, and deeper knowledge of distributed systems concepts like consensus algorithms and eventual consistency."
