import json
import sys

def get_session_id():
    try:
        data = json.loads(sys.stdin.read())
        return data.get('session_id', '')
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}", file=sys.stderr)
        return ''
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return ''

if __name__ == '__main__':
    print(get_session_id())
