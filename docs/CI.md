# CI / CD

Everything in this document is enforced by workflows in `.github/workflows/`.

| Workflow | File | Trigger | Purpose |
| --- | --- | --- | --- |
| `NEXUS-OSINT CI` | `ci.yml` | push to `main` / `arena/**`, PR to `main`, manual | Test, typecheck, build and container-build the whole stack |
| `NEXUS-OSINT CD` | `cd.yml` | tag `v*.*.*`, manual | Publish multi-arch images to GHCR, scan them, open a GitHub release |
| `CodeQL` | `codeql.yml` | push, PR, weekly | Static analysis for Python and TypeScript |
| `Security` | `security.yml` | PR, weekly, manual | Dependency review, `pip-audit`, `npm audit`, advisory agent audit |

## Required checks

Branch protection should require **`CI gate`**. It fans in every other job,
so new jobs are covered without touching the rule:

- `backend` — byte-compile, `pytest`, `pip-audit` (fails on known CVEs)
- `frontend` — `npm ci`, ESLint, `tsc --noEmit`, `next build`, `npm audit`
  (production and full tree, failing at `high`)
- `agent` — byte-compile and dependency-graph resolution for the agent service
- `docker` — compose manifest validation plus cached image builds for backend
  and frontend

## Running CI locally

```bash
make ci        # the same checks the pipeline runs
make audit     # dependency audits only
```

Individual targets: `make ci-backend`, `make ci-frontend`, `make ci-agent`,
`make ci-docker`.

## Dependency policy

- Python and npm dependencies are pinned exactly (`requirements.txt`,
  `package.json`) and locked (`package-lock.json`).
- Any `high`/`critical` advisory in production dependencies fails the build.
- `moderate` advisories in ESLint-only tooling are tolerated for now; they are
  development-only and sit behind `eslint-plugin-*` peer ranges that cap at
  ESLint 9, so moving to ESLint 10 has to wait for those plugins.

## Known advisory backlog (agent service)

`agent/requirements.txt` pins the LangChain/LangGraph 0.2/0.1 generation
together with `sentence-transformers`, which drags in `transformers` 4.x.
Advisories exist for that stack:

- `langchain` / `langchain-core` / `langchain-text-splitters` / `langsmith`
- `transformers` (fixes only exist in the 5.x line)

Fixing these requires a coordinated LangGraph 1.x + Transformers 5.x migration
and new tests for the agent graph. Until then the audit runs weekly as
**advisory only** (`agent-audit` job, report uploaded as an artifact) and does
not block pull requests. `fastapi`, `pydantic` and `uvicorn` were upgraded so
the `starlette` advisories no longer apply.

## Releasing

```bash
git tag v3.6.0
git push origin v3.6.0
```

This publishes:

- `ghcr.io/<owner>/<repo>-backend:<version>` and `:latest`
- `ghcr.io/<owner>/<repo>-frontend:<version>` and `:latest`

with SBOM and provenance attestations, a Trivy scan (report only, so a base
image advisory never blocks a release), and a GitHub release with generated
notes. `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_WS_URL` are read from repository
variables when building the frontend image.

## Automation

`dependabot.yml` opens weekly grouped updates for Actions, pip (backend and
agent), npm and Docker base images. Dependabot PRs run the full pipeline and
`dependency-review` before they can merge.
