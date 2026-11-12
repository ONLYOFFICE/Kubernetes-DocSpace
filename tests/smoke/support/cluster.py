"""Kubernetes pods and deployments as seen by kubectl."""
import json
import subprocess

SUCCEEDED = "Succeeded"
KUBECTL_TIMEOUT = 60  # seconds, an unreachable API server must not hang the run
ROLLOUT_TIMEOUT = 300  # seconds to wait for one deployment to become ready again

# The services that keep the portal data. The router is left alone: the port-forward
# of the run is bound to its pod, so restarting it would cut the tests off the portal.
RESTARTED_DEPLOYMENTS = ("api", "api-system", "files", "files-worker", "studio", "people-server")


def kubectl(*args, timeout=KUBECTL_TIMEOUT):
    """Output of a kubectl call; a failed call raises with its error text."""
    result = subprocess.run(
        ["kubectl", *args], capture_output=True, text=True, check=True, timeout=timeout,
    )
    return result.stdout


def fetch_pods(namespace):
    """All pods of the namespace as parsed `kubectl get pods -o json` items."""
    return json.loads(kubectl("get", "pods", "-n", namespace, "-o", "json"))["items"]


def restart_deployments(namespace, names):
    """Restart the deployments and wait until every one of them is ready again."""
    targets = [f"deployment/{name}" for name in names]
    kubectl("rollout", "restart", *targets, "-n", namespace)
    for target in targets:
        kubectl(
            "rollout", "status", target, "-n", namespace, f"--timeout={ROLLOUT_TIMEOUT}s",
            timeout=ROLLOUT_TIMEOUT + KUBECTL_TIMEOUT,
        )


def running_pods(pods):
    """Completed jobs (db init, etc.) are expected to be not Ready, so they are left out."""
    return [pod for pod in pods if pod["status"]["phase"] != SUCCEEDED]


def is_ready(pod):
    conditions = pod["status"].get("conditions", [])
    return any(c["type"] == "Ready" and c["status"] == "True" for c in conditions)


def restart_count(pod):
    return sum(c["restartCount"] for c in pod["status"].get("containerStatuses", []))
