import subprocess
import json
import sys

def check_health():
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:5050/health"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"Error executing curl: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)

        response = json.loads(result.stdout)
        entries = response.get("entries", {})

        for component, details in entries.items():
            if details.get("status") != "Healthy":
                print(f"Unhealthy component detected: {component}", file=sys.stderr)
                sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    check_health()
