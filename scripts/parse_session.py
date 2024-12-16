import json
import sys

def get_session_id():
    try:
        data = json.loads(sys.stdin.read())

        # Check for error response
        if 'detail' in data:
            error_detail = data['detail']
            if isinstance(error_detail, dict):
                print(f"Error: {error_detail.get('error', 'Unknown error')}: {error_detail.get('message', 'No message')}", file=sys.stderr)
            else:
                print(f"Error: {error_detail}", file=sys.stderr)
            return ''

        # Handle successful response
        session_id = data.get('session_id')
        if not session_id:
            print("Error: No session ID found in response", file=sys.stderr)
            return ''

        return session_id

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return ''
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return ''

if __name__ == '__main__':
    print(get_session_id())
