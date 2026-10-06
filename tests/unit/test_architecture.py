import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "src"
PACKAGES = next(p for p in SRC.iterdir() if (p / "__init__.py").exists())
LAYERS = [
    "core",
    "ports",
    "adapters",
    "pipeline",
    "eval"
]


def test_layer_folder_exists():
    for layer in LAYERS:
        assert (PACKAGES / layer).is_dir()
        
def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif (isinstance(node, ast.ImportFrom)):
            if node.module:
                found.add(node.module)
    return found
        
def test_imported_modules_finds_absolute_imports(tmp_path):
    f = tmp_path / "x.py"
    f.write_text("import os\nfrom adaptrag.core import models\n")
    assert imported_modules(f) == {"os", "adaptrag.core"}