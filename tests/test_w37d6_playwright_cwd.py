from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "web/playwright.config.js"


def test_playwright_backend_starts_from_project_root():
    text = CONFIG.read_text(encoding="utf-8")

    assert (
        "cd .. && PYTHONPATH=. venv/bin/python -m uvicorn "
        "app.main:app"
    ) in text


def test_playwright_does_not_use_old_web_cwd_backend_command():
    text = CONFIG.read_text(encoding="utf-8")

    assert (
        "PYTHONPATH=.. ../venv/bin/python -m uvicorn"
        not in text
    )
