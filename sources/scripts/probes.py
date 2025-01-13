import subprocess
import json
import logging
import sys
import socket

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
        pod_name = socket.gethostname()
        result = subprocess.run(
            ["curl", "-s", "http://localhost:5050/health"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"Error executing healthcheck in pod {pod_name}: {result.stderr.strip()}")
            sys.exit(1)

        response = json.loads(result.stdout)

        unhealthy_components = []
        for component, details in response.get("entries", {}).items():
            if details.get("status") != "Healthy":
                unhealthy_components.append(component)

        if unhealthy_components:
            log_message = (
                f"Pod {pod_name} - Unhealthy components: {', '.join(unhealthy_components)}\n"
                f"Response: {json.dumps(response)}"
            )
            logger.error(log_message)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error in pod {pod_name}: {e}")
        sys.exit(1)

logger = init_logger('health_checker')
check_health()
