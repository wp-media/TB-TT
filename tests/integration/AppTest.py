"""
    Integration tests for the app.py main file
"""

from pathlib import Path
import runpy
import pytest


def test_main_script():
    """
        Checks that the main script app.py runs correctly up until starting the Flask app
        (not tested based on the __name__ condition).
        This ensure that the setup is completed without errors.
    """
    try:
        runpy.run_path(Path(__file__).parent.parent.parent / "app.py")
    # pylint: disable-next=broad-exception-caught
    except Exception:
        pytest.fail("An error occured while running app.py.")
