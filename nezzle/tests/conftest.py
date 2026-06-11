import os

# All tests run headless: the offscreen platform never creates real windows.
# This must be set before the first Qt import of the session; pytest imports
# conftest.py before any test module, so this is the right place.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="session")
def qapp():
    """Session-wide offscreen QApplication.

    Reuses the instance that older test modules create at import time, so it
    is safe regardless of which module pytest imports first.
    """
    from qtpy.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app
