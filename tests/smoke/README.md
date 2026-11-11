# DocSpace smoke tests

Python tests that run against an installed DocSpace: the portal API behind the router, and the Kubernetes cluster it runs in.
The `Smoke install` workflow (`.github/workflows/smoke.yaml`) installs the chart into a kind cluster and runs them.

## Layout

| Path | What it holds | Needs |
|---|---|---|
| `core/` | Portal availability, public API, authentication, files, rooms, sharing, OAuth | nothing special, fits any configuration |
| `docs/` | Document Server: document creation, conversion, editor config | Docs in the install |
| `cluster/` | Pod health and data persistence after a restart of the services | `kubectl` access to the cluster |
| `values/` | Helm values of an install, one file per configuration (`minimal.yaml`) | |
| `conftest.py` | Fixtures: `portal` (anonymous, per test), `settings`, `wizard_completed`, `admin` (owner session), `pods` | |
| `support/` | Helpers: `config` (environment), `endpoints` (API paths), `constants` (titles, codes, JSON keys), `client` (`Portal`), `auth`, `files`, `oauth`, `cluster`, `readiness` | |

A configuration is a values file plus the folders that fit it. There are no markers: to skip what a configuration lacks, leave its folder out of the command.

The first test that needs the owner runs the first-run wizard once (`wizard_completed`); on a portal that is already set up the wizard is skipped
and the owner from `PORTAL_EMAIL` and `PORTAL_PASSWORD` is used.

## Run locally

```bash
pip install -r tests/smoke/requirements.txt
BASE_URL=http://localhost:8092 LICENSE_FILE=/path/to/license.lic pytest tests/smoke
```

Useful selections:

```bash
pytest tests/smoke/core tests/smoke/docs tests/smoke/cluster   # everything, in the order CI uses
pytest tests/smoke/core                                        # without Docs and without kubectl
pytest tests/smoke/core/test_files_and_folders.py              # one file
pytest tests/smoke -k conversion                               # by name
```

Keep `cluster` last: its persistence test restarts the DocSpace services. The tests in `cluster/` call `kubectl`, so they need access to the cluster DocSpace runs in.

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `BASE_URL` | `http://localhost:8092` | Portal address reachable from the machine running the tests |
| `NAMESPACE` | `default` | Namespace DocSpace is installed in |
| `PORTAL_EMAIL`, `PORTAL_PASSWORD` | `smoke@smoke.com`, `Smoke-Test-2026` | Owner created by the wizard |
| `LICENSE_FILE` or `LICENSE` | none | License path or content; DocSpace Enterprise requires one |
| `EXPECTED_VERSION` | none | Portal version to expect, for example `3.7.2`; the version test is skipped without it |

## In CI

- The license comes from the repository secret `DOCSPACE_LICENSE_B64`, the `license.lic` file encoded with `base64`. The step `Prepare license` decodes it.
- `Run smoke tests` writes `smoke-report.xml`. `Smoke summary` turns it into one `[OK]` or `[FAIL]` line plus a table of all tests on the run page.
- On failure `Collect compact cluster diagnostics` adds `smoke-diagnostics.txt`. Both files go to the artifact `smoke-report`.
- To print the same summary for any run:

```bash
python .github/scripts/smoke_report.py fetch <run-id> --repo ONLYOFFICE/Kubernetes-DocSpace
```

This needs the GitHub CLI `gh`.

## Adding a test

1. Put API paths into `support/endpoints.py` and titles, codes and JSON keys into `support/constants.py`, so the test body has no literals.
2. Put repeated scenarios into `support/` and keep the test itself to the steps and the assertion.
3. Give the test a one-line docstring: the run summary shows it as the test name.
4. Put the test into the folder that matches what it needs: `core/` when it works with any configuration, `docs/` when it needs Document Server, `cluster/` when it needs `kubectl`. A new need gets a new folder.

## Adding a configuration

Put the Helm values into `values/<name>.yaml`, install with `-f tests/smoke/values/<name>.yaml` and run the folders that fit it. `values/minimal.yaml` is what the workflow installs now.
