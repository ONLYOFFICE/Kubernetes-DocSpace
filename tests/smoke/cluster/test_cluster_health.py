"""Kubernetes-level health: every pod is up and stable."""
from support.cluster import is_ready, restart_count, running_pods


def test_all_pods_are_ready(pods):
    """Every pod that is meant to keep running is Ready."""
    not_ready = [pod["metadata"]["name"] for pod in running_pods(pods) if not is_ready(pod)]

    assert not not_ready, f"pods not Ready: {not_ready}"


def test_no_pod_has_restarted(pods):
    """No container has restarted since the install."""
    restarted = {pod["metadata"]["name"]: restart_count(pod) for pod in pods if restart_count(pod) > 0}

    assert not restarted, f"pods with container restarts: {restarted}"
