# -*- coding: utf-8 -*-
import enum

from qtpy.QtCore import Qt

DEFAULT_SCENE_WIDTH = 1000
DEFAULT_SCENE_HEIGHT = 1000


#class Lock(enum.IntFlag):
class Lock(object):
    """
    For bitwise operations, do not use Enum class
    """
    NODES = 1
    LINKS = 2
    LABELS = 4


#class DataRole(enum.IntEnum):
class DataRole(object):
    InitStatusRole = Qt.UserRole + 1
