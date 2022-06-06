import os
from os.path import join
from os.path import dirname
from os.path import abspath
import sys
import importlib


def reload_modules(dirs=None, modules=None):
    """Reload modules in a directory

    Args:
        dirs:
        modules:

    """
    if not dirs:
        dirs = ["."]
    elif isinstance(dirs, str):
        dirs = [dirs]

    for dpath in dirs:
        dpath = abspath(dpath)
        if os.path.isfile(dpath):
            dpath = dirname(dpath)

        if dpath not in sys.path:
            sys.path.append(dpath)
            
        if not modules:
            modules = []
            for fname in os.listdir(dpath):
                modname, ext = os.path.splitext(fname)
                if ext != ".py":
                    continue
                modules.append(modname)

        for modname in modules:
            mod = importlib.import_module(modname)
            importlib.reload(mod)