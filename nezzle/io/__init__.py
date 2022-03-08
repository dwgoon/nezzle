
import os

from nezzle.io.sif import read_metadata_from_sif
from nezzle.io.sif import read_sif
from nezzle.io.sif import write_sif

from nezzle.io.nzj import read_metadata_from_nzj
from nezzle.io.nzj import read_nzj
from nezzle.io.nzj import write_nzj

# from nezzle.io.cytoscape import read_metadata_from_cx
# from nezzle.io.cytoscape import read_cx
# from nezzle.io.cytoscape import write_cx


from nezzle.io.image import write_image


def read_metadata(fpath):
    if not fpath:
        raise ValueError("Invalid file path: %s"%(fpath))

    file_name_ext = os.path.basename(fpath)
    fname, fext = os.path.splitext(file_name_ext)

    if file_name_ext.endswith('.sif'):
        return read_metadata_from_sif(fpath)
    elif file_name_ext.endswith('.nzj') or file_name_ext.endswith('.json'):
        return read_metadata_from_nzj(fpath)

    else:
        raise ValueError("Unsupported file type: %s"%(fext))


def read_network(fpath, edge_map=None):
    if not fpath:
        raise ValueError("Invalid file path: %s"%(fpath))
    file_name_ext = os.path.basename(fpath)
    fname, fext = os.path.splitext(file_name_ext)

    if file_name_ext.endswith('.sif'):
        return read_sif(fpath, edge_map)
    elif file_name_ext.endswith('.nzj') or file_name_ext.endswith('.json'):
        return read_nzj(fpath, edge_map)

    else:
        raise ValueError("Unsupported file type: %s"%(fext))
# end of read_network


def write_network(net, fpath):
    file_name_ext = os.path.basename(fpath)
    file_name_ext = file_name_ext.casefold()

    if file_name_ext.endswith('.sif'):
        write_sif(net, fpath)
    elif file_name_ext.endswith('.nzj') or file_name_ext.endswith('.json'):
        write_nzj(net, fpath)
    else:
        raise ValueError("Unsupported file type: %s" % (file_name_ext))