import json
import codecs
from collections import defaultdict

import numpy as np

from nezzle.graphics import Network


class NpEncoder(json.JSONEncoder):
    """
    [Reference] https://stackoverflow.com/a/57915246
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
# end of class

def read_metadata_from_nzj(fpath):
    metadata = {}
    interactions = defaultdict(int)
    with codecs.open(fpath, "r", encoding="utf-8") as fin:
        dict_net = json.loads(fin.read())

    for edge in dict_net["EDGES"]:
        str_head_type = edge["HEAD"]["ITEM_TYPE"].title()
        interactions[str_head_type] += 1

    metadata["NETWORK_NAME"] = dict_net["NAME"]
    metadata["INTERACTIONS"] = interactions
    return metadata
# end of def


def read_nzj(fpath, edge_map):
    with codecs.open(fpath, "r", encoding="utf-8") as fin:
        dict_net = json.loads(fin.read())

        for edge in dict_net["EDGES"]:
            head_type_ori = edge["HEAD"]["ITEM_TYPE"].title()
            head_type_new = edge_map[head_type_ori]
            edge["HEAD"]["ITEM_TYPE"] = head_type_new.upper()

    return Network.from_dict(dict_net)
# end of def


def write_nzj(net, fpath):
    with codecs.open(fpath, "w", encoding="utf-8") as fout:
        fout.write(json.dumps(net.to_dict(), cls=NpEncoder))
# end of def
