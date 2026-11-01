import sys
import subprocess
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

def test_fitness_functions_allowed_to_use():
    result = subprocess.run(
        [sys.executable, "-c", "import importlinter.cli, sys; sys.exit(importlinter.cli.lint_imports())"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    print(f"\n{result.stdout}")
    assert result.returncode == 0, f"Violação da arquitetura detetada:\n{result.stdout}\n{result.stderr}"