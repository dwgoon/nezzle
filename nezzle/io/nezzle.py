import json
import codecs
from collections import defaultdict

from nezzle.graphics import Network


def read_metadata_from_nzjs(fpath):
    metadata = {}
    interactions = defaultdict(int)
    with codecs.open(fpath, "r", encoding="utf-8") as fin:
        dict_net = json.loads(fin.read())

    for link in dict_net["LINKS"]:
        str_head_type = link["HEAD"]["TYPE"].title()
        interactions[str_head_type] += 1

    metadata["NETWORK_NAME"] = dict_net["NAME"]
    metadata["INTERACTIONS"] = interactions
    return metadata
# end of def


def read_nzjs(fpath, link_map):
    with codecs.open(fpath, "r", encoding="utf-8") as fin:
        dict_net = json.loads(fin.read())

        for link in dict_net["LINKS"]:
            head_type_ori = link["HEAD"]["TYPE"].title()
            head_type_new = link_map[head_type_ori]
            link["HEAD"]["TYPE"] = head_type_new.upper()

    return Network.from_dict(dict_net)
# end of def


def write_nzjs(net, fpath):
    with codecs.open(fpath, "w", encoding="utf-8") as fout:
        fout.write(json.dumps(net.to_dict()))
# end of def
