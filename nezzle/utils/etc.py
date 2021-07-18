import os


def extract_name_and_ext(fpath):
    fpath = fpath.strip()
    fname, fext = os.path.splitext(fpath)
    fext = fext.strip('.')
    return fname, fext