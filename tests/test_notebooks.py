"""Test Jupyter notebooks in examples/ directory."""
from __future__ import annotations
import pytest
from pathlib import Path

# Skip all tests in this module if nbmake is not installed
pytest.importorskip("nbmake", reason="nbmake not installed - install with: pip install nbmake")

# Also need nbformat to read notebooks
nbformat = pytest.importorskip("nbformat", reason="nbformat not installed")
from nbclient import NotebookClient


@pytest.mark.parametrize(
    "notebook_path",
    [
        "examples/workbook.ipynb",
    ],
)
def test_notebook_execution(notebook_path):
    """Test that notebooks execute without errors using nbclient."""
    nb_path = Path(notebook_path)
    assert nb_path.exists(), f"Notebook not found: {notebook_path}"

    # Read the notebook
    with open(nb_path) as f:
        nb = nbformat.read(f, as_version=4)

    # Execute the notebook from its directory
    # This ensures relative paths in the notebook work correctly
    notebook_dir = nb_path.parent
    client = NotebookClient(
        nb,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": str(notebook_dir)}}
    )

    try:
        client.execute()
    except Exception as e:
        pytest.fail(f"Notebook {notebook_path} failed to execute: {e}")
