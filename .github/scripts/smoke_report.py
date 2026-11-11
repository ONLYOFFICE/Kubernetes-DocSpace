#!/usr/bin/env python3
"""Compact report of a smoke run, built from the JUnit XML (and optional cluster diagnostics).

Usage:
    smoke_report.py summary [--xml smoke-report.xml] [--diagnostics smoke-diagnostics.txt]
                            [--run-id ID] [--github-summary PATH]
    smoke_report.py fetch RUN_ID [--repo OWNER/NAME]     (needs the GitHub CLI `gh`)

Output budget: one line on success, at most MAX_LINES lines on failure.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

MAX_LINES = 50
DIAGNOSTICS_LINES = 24
MAX_LINE_WIDTH = 200
TRACEBACK_LINES = 20
DETAIL_LINES = 6
ARTIFACT_NAME = "smoke-report"
REPORT_FILE = "smoke-report.xml"
DIAGNOSTICS_FILE = "smoke-diagnostics.txt"

SECRET_PATTERNS = [
    (re.compile(r'("(?:token|wizardToken|passwordHash|salt)"\s*:\s*")[^"]+'), r"\1***"),
    (re.compile(r"(Authorization:\s*)\S+", re.IGNORECASE), r"\1***"),
]


def mask(text):
    """Hide tokens and password material that may appear in assertion messages."""
    for pattern, replacement in SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def clip(line):
    line = mask(line.rstrip())
    return line if len(line) <= MAX_LINE_WIDTH else line[: MAX_LINE_WIDTH - 3] + "..."


def read_results(xml_path):
    """Counters plus the list of failed testcases (name, assertion, traceback lines)."""
    root = ET.parse(xml_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    counters = {key: int(suite.get(key, 0)) for key in ("tests", "failures", "errors", "skipped")}
    counters["time"] = float(suite.get("time", 0))
    failed = []
    for case in suite.iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is None:
            continue
        text = (problem.text or problem.get("message") or "").splitlines()
        assertions = [line[1:].strip() for line in text if line.startswith("E ")]
        failed.append({
            "name": f"{case.get('classname', '')}::{case.get('name', '')}".lstrip(":"),
            "assertion": assertions[0] if assertions else " ".join((problem.get("message") or "").splitlines()[:1]),
            "details": assertions[1:],
            "traceback": [line for line in text if line.strip()],
        })
    counters["passed"] = counters["tests"] - counters["failures"] - counters["errors"] - counters["skipped"]
    return counters, failed


FRAME_START = re.compile(r"^\S.*:\d+: in ")
LIBRARY_PATH = re.compile(r"site-packages|[\/]lib[\/]python", re.IGNORECASE)


def project_frames(lines):
    """Traceback lines without the frames of libraries (requests, urllib3, pytest internals)."""
    kept, keep = [], True
    for line in lines:
        if FRAME_START.match(line):
            keep = not LIBRARY_PATH.search(line)
        if keep and not line.startswith("E "):
            kept.append(line)
    return kept


def format_duration(seconds):
    minutes, rest = divmod(round(seconds), 60)
    return f"{minutes}m {rest}s" if minutes else f"{rest}s"


def headline(counters, run_id):
    bad = counters["failures"] + counters["errors"]
    # A run in which no test passed verified nothing (nothing collected, or everything skipped).
    icon = "OK" if bad == 0 and counters["passed"] > 0 else "FAIL"
    parts = [f"{counters['passed']} passed", f"{bad} failed"]
    if counters["skipped"]:
        parts.append(f"{counters['skipped']} skipped")
    if icon == "FAIL" and bad == 0:
        parts.append("nothing was verified")
    run = f" (run {run_id})" if run_id else ""
    return f"[{icon}] smoke: {', '.join(parts)} in {format_duration(counters['time'])}{run}"


def read_diagnostics(path):
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8", errors="replace") as handle:
        return [clip(line) for line in handle.read().splitlines() if line.strip()]


def build_report(xml_path, diagnostics_path, run_id):
    """Report lines; a single line when everything passed."""
    if not os.path.isfile(xml_path):
        lines = [f"[FAIL] smoke: no {os.path.basename(xml_path)}, the job failed before the tests ran"
                 + (f" (run {run_id})" if run_id else "")]
        diagnostics = read_diagnostics(diagnostics_path)[:DIAGNOSTICS_LINES]
        if diagnostics:
            lines.append("cluster diagnostics:")
            lines.extend(f"  {line}" for line in diagnostics)
        return lines[:MAX_LINES]
    counters, failed = read_results(xml_path)
    lines = [headline(counters, run_id)]
    if not failed:
        return lines

    diagnostics = read_diagnostics(diagnostics_path)[:DIAGNOSTICS_LINES]
    budget = MAX_LINES - len(lines) - (len(diagnostics) + 1 if diagnostics else 0)

    # Tests that fail for the same reason (e.g. a broken fixture) are reported once.
    groups = {}
    for item in failed:
        groups.setdefault(item["assertion"], []).append(item)
    per_group = max(4, budget // len(groups))
    shown = list(groups.values())[: max(1, budget // 4)]
    for items in shown:
        first = items[0]
        extra = f" (+{len(items) - 1} with the same error)" if len(items) > 1 else ""
        lines.append(f"FAILED {first['name']}{extra}")
        lines.append(f"  {clip(first['assertion'])}")
        if len(items) > 1:
            lines.append(clip("  also: " + ", ".join(item["name"].split("::")[-1] for item in items[1:])))
        details = [clip(line) for line in first["details"][:DETAIL_LINES]]
        lines.extend(f"    {line}" for line in details)
        trace = [clip(line) for line in project_frames(first["traceback"])]
        lines.extend(f"  | {line}" for line in trace[: min(TRACEBACK_LINES, max(0, per_group - 3 - len(details)))])
    if len(groups) > len(shown):
        hidden = sum(len(items) for items in list(groups.values())[len(shown):])
        lines.append(f"... and {hidden} more failed tests with other errors")
    if diagnostics:
        lines.append("cluster diagnostics:")
        lines.extend(f"  {line}" for line in diagnostics)
    return lines[:MAX_LINES]


def humanize(text):
    """test_owner_can_log_in -> Owner can log in."""
    text = text.removeprefix("test_").replace("_", " ").strip()
    return text[:1].upper() + text[1:]


def case_title(case):
    """Docstring of the test (recorded by conftest), else its humanized function name."""
    for prop in case.iter("property"):
        if prop.get("name") == "description" and prop.get("value"):
            return prop.get("value").rstrip(".")
    return humanize(case.get("name", "").split("[")[0])


def read_cases(xml_path):
    """Every testcase as (area, title, status, seconds); failed ones first, the rest in run order."""
    root = ET.parse(xml_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    cases = []
    for case in suite.iter("testcase"):
        if case.find("failure") is not None or case.find("error") is not None:
            status = "FAILED"
        elif case.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"
        area = humanize(case.get("classname", "").split(".")[-1])
        title = case_title(case)
        name = case.get("name", "")
        param = name[name.find("["):] if "[" in name else ""
        cases.append([area, title, param, status, float(case.get("time", 0))])
    # A parametrized test shares its title between cases, so keep the parameter there to tell them apart.
    titles = [item[1] for item in cases]
    result = [(area, title + (f" {param}" if titles.count(title) > 1 else ""), status, seconds)
              for area, title, param, status, seconds in cases]
    return sorted(result, key=lambda item: item[2] != "FAILED")


def cases_table(cases):
    """Collapsible markdown table of all tests for the run page."""
    pipe = "\\|"  # a pipe inside a cell would split the table row
    rows = [f"| {area} | {title.replace('|', pipe)} | {status} | {seconds:.1f}s |"
            for area, title, status, seconds in cases]
    return "\n".join([
        f"<details><summary>All tests ({len(cases)})</summary>",
        "",
        "| Area | Test | Result | Time |",
        "| --- | --- | --- | --- |",
        *rows,
        "",
        "</details>",
    ])


def command_summary(args):
    lines = build_report(args.xml, args.diagnostics, args.run_id)
    print("\n".join(lines))
    if args.github_summary:
        # A fence inside an error text would close the code block early.
        page = "```\n" + "\n".join(lines).replace("```", "'''") + "\n```\n"
        if os.path.isfile(args.xml):
            page += "\n" + cases_table(read_cases(args.xml)) + "\n"
        with open(args.github_summary, "a", encoding="utf-8") as handle:
            handle.write(page)
    return 0 if lines[0].startswith("[OK]") else 1


def command_fetch(args):
    if not shutil.which("gh"):
        print("GitHub CLI `gh` is not installed: https://cli.github.com/", file=sys.stderr)
        return 2
    repo = ["--repo", args.repo] if args.repo else []
    with tempfile.TemporaryDirectory() as directory:
        downloaded = subprocess.run(
            ["gh", "run", "download", args.run_id, "-n", ARTIFACT_NAME, "-D", directory, *repo],
            capture_output=True, text=True,
        )
        if downloaded.returncode != 0:
            print(f"[FAIL] smoke: no artifact '{ARTIFACT_NAME}' in run {args.run_id}, last failed log lines:")
            logs = subprocess.run(["gh", "run", "view", args.run_id, "--log-failed", *repo],
                                  capture_output=True, text=True)
            print("\n".join(clip(line) for line in logs.stdout.splitlines()[-30:]))
            return 1
        args.xml = os.path.join(directory, REPORT_FILE)
        args.diagnostics = os.path.join(directory, DIAGNOSTICS_FILE)
        args.github_summary = None
        return command_summary(args)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    summary = commands.add_parser("summary", help="build the report from local files")
    summary.add_argument("--xml", default=REPORT_FILE)
    summary.add_argument("--diagnostics", default=DIAGNOSTICS_FILE)
    summary.add_argument("--run-id", default=os.environ.get("GITHUB_RUN_ID"))
    summary.add_argument("--github-summary", default=os.environ.get("GITHUB_STEP_SUMMARY"))
    summary.set_defaults(handler=command_summary)

    fetch = commands.add_parser("fetch", help="download the artifact of a GitHub run and report")
    fetch.add_argument("run_id")
    fetch.add_argument("--repo")
    fetch.set_defaults(handler=command_fetch)

    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
