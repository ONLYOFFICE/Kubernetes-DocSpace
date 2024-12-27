import subprocess
import json
import logging
import sys

def init_logger(name):
    logger = logging.getLogger(name)
    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logger.setLevel(logging.DEBUG)
    stderr = logging.StreamHandler(sys.stderr)
    stderr.setFormatter(logging.Formatter(formatter))
    stderr.setLevel(logging.DEBUG)
    logger.addHandler(stderr)
    return logger

def check_health():
    try:
        result = subprocess.run(
            ["curl", "-s", "http://localhost:5050/health"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Error executing healthcheck: {result.stderr.strip()}")
            sys.exit(1)

        response = json.loads(result.stdout)

        unhealthy_components = []
        for component, details in response.get("entries", {}).items():
            if details.get("status") != "Healthy":
                colored_component = f"\033[31m{component}\033[0m"
                unhealthy_components.append(colored_component)

        if unhealthy_components:
            logger.error("Unhealthy components: " + ", ".join(unhealthy_components))
            logger.error(json.dumps(response))
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

logger = init_logger('health_checker')
check_health()
