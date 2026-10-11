# W41-D2 G0 Baseline Acceptance

## 1. Baseline Identity

- Date: 2026-10-11
- Branch: main
- Baseline commit: e35f396f6b14b2f634b810828858e6b97cf5547f
- Previous W41-D1 audit: completed and pushed
- Repository worktree before verification: clean

## 2. Execution Environment

- Python: 3.12.3
- Environment: ~/hs_agent/venv
- pytest: 9.1.1
- numpy: 2.4.6
- pydantic: 2.13.4
- fastapi: 0.141.1
- starlette: 1.3.1
- httpx: 0.28.1
- pip check: PASS, exit code 0

Optimization packages not installed:
- scipy
- pymoo
- pyswarms
- deap

## 3. Full Regression

Command:
venv/bin/python -m pytest -q

Result:
- 1081 passed
- 1 warning
- 0 failures
- Exit code: 0
- Duration: 31.09 seconds

Matches the historical W40-D6 passed-test count.

Evidence:
W41D2_full_pytest.log

## 4. Numerical Regression

Scope:
Six W39/W40 numerical test files covering
benchmarks, closure, branch resolution,
integration, angle sweep and E-point propagation.

Result:
- 123 passed
- Exit code: 0
- Duration: 0.20 seconds

These 123 tests are included within the
full regression suite and must not be double-counted.

Evidence:
W41D2_numerical_pytest.log

## 5. Warning

Observed:
StarletteDeprecationWarning in FastAPI test client.

Decision:
Track as a dependency compatibility warning.
Do not change dependency versions during G0.

## 6. Engineering Limitations

- ER-001 remains NOT_SOLVER_READY.
- No verified engineering optimization bounds.
- No rear-link-angle to support-height mapping.
- No independently constrained top-beam pose.
- No physical beam-tip T trajectory.
- No complete operating-height 80 mm verification.
- Synthetic benchmarks are not physical validation.

## 7. G0 Decision

Software baseline:
PASS_SOFTWARE_BASELINE

Engineering reference:
ENGINEERING_REFERENCE_NOT_READY

Permitted next work:
- W41-D3 design variable contract
- Optimization parameter and boundary definition
- Continued synthetic-domain software validation

Not yet permitted:
- Claim verified hydraulic-support performance
- Claim 80 mm beam-tip compliance
- Promote synthetic results to engineering evidence

## 8. Evidence Scope

This decision is based on the observed
W41-D2 terminal test results and dependency audit.

It does not represent independent physical testing
or verification against a complete engineering reference.
