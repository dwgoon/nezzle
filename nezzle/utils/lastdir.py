"""
Remember the last directory used by file dialogs.

Stored via QSettings, so the location survives not only the current run
but also application restarts.
"""

import os

from qtpy.QtCore import QSettings

__all__ = ["get_last_dir", "set_last_dir"]

_ORG = "nezzle"
_APP = "nezzle"


def get_last_dir(key):
    """Return the last directory used for the given dialog kind
    (e.g. 'network', 'image', 'code'), or '' if none was recorded.
    An empty string makes QFileDialog fall back to its default location.
    """
    settings = QSettings(_ORG, _APP)
    dpath = settings.value("last_dir/%s" % key, "", type=str)
    return dpath if os.path.isdir(dpath) else ""


def set_last_dir(key, fpath):
    """Record the directory of fpath as the last used one for key."""
    dpath = os.path.dirname(os.path.abspath(fpath))
    if os.path.isdir(dpath):
        settings = QSettings(_ORG, _APP)
        settings.setValue("last_dir/%s" % key, dpath)
