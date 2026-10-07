import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"
PACKAGE = next(p for p in SRC.iterdir() if (p / "__init__.py").exists())
LAYERS = ["core", "ports", "adapters", "pipeline", "eval"]

ALLOWED = {
    "core": set(),
    "ports": {"core"},
    "adapters": {"core", "ports"},
    "pipeline": {"core", "ports"},
    "eval": {"core", "ports"},
}


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                found.add(node.module)
    return found


def layer_of(module: str) -> str | None:
    parts = module.split(".")
    if parts[0] == PACKAGE.name and len(parts) > 1 and parts[1] in LAYERS:
        return parts[1]
    return None


def violations(layer: str) -> list[str]:
    problems = []
    allowed = ALLOWED[layer] | {layer}
    for file in (PACKAGE / layer).rglob("*.py"):
        for module in imported_modules(file):
            target = layer_of(module)
            if target is not None and target not in allowed:
                problems.append(f"{file.relative_to(SRC)} imports {module}")
    return problems


def test_layer_folders_exist():
    for layer in LAYERS:
        assert (PACKAGE / layer).is_dir()


def test_imported_modules_finds_absolute_imports(tmp_path):
    f = tmp_path / "x.py"
    f.write_text("import os\nfrom adaptrag.core import models\n")
    assert imported_modules(f) == {"os", "adaptrag.core"}


def test_layer_of():
    assert layer_of("adaptrag.core.models") == "core"
    assert layer_of("adaptrag.adapters") == "adapters"
    assert layer_of("os") is None
    assert layer_of("adaptrag") is None


@pytest.mark.parametrize("layer", LAYERS)
def test_layer_respects_dependency_rule(layer):
    assert violations(layer) == []