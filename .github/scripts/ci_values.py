#!/usr/bin/env python3
"""Print Helm values that lower the CPU requests of every service in values.yaml.

The smoke install puts about thirty pods on the single node of a kind cluster, and with the default
requests (about 4 CPUs in total) the last pod stays Pending with `Insufficient cpu`. Limits and memory
requests are left as they are, only the amount the scheduler reserves is cut down.

Usage:
    ci_values.py [values.yaml] > ci-values.yaml
"""
import sys

import yaml

CPU_REQUEST = "20m"


def lowered_requests(node):
    """Nested overrides for every mapping that has `resources.requests.cpu`, None when there are none."""
    if not isinstance(node, dict):
        return None
    overrides = {}
    for key, value in node.items():
        if key == "resources":
            requests = value.get("requests") if isinstance(value, dict) else None
            if isinstance(requests, dict) and "cpu" in requests:
                overrides[key] = {"requests": {"cpu": CPU_REQUEST}}
        else:
            nested = lowered_requests(value)
            if nested:
                overrides[key] = nested
    return overrides or None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "values.yaml"
    with open(path, encoding="utf-8") as handle:
        values = yaml.safe_load(handle)
    yaml.safe_dump(lowered_requests(values) or {}, sys.stdout, default_flow_style=False)


if __name__ == "__main__":
    main()
