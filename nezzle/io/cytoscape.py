import os
import re
import json
import codecs
from collections import defaultdict
import warnings

import networkx as nx
from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtGui import QColor

from nezzle.graphics import NodeClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import Network
from nezzle.utils.math import rotate, dist, internal_division
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT


from nezzle.graphics import Network


# def read_metadata_from_cx(fpath):
#     with codecs.open(fpath, "r", encoding="utf-8") as fin:
#         cxjson = json.loads(fin.read())
#
#     reader = CxJsonReader()
#     g = reader.read(cxjson)
#
#     metadata = {}
#     interactions = defaultdict(int)
#
#     for edge in dict_net["EDGES"]:
#         str_head_type = edge["HEAD"]["ITEM_TYPE"].title()
#         interactions[str_head_type] += 1
#
#     metadata["NETWORK_NAME"] = dict_net["NAME"]
#     metadata["INTERACTIONS"] = interactions
#     return metadata
# # end of def
#
#
# def read_cx(fpath, edge_map):
#     with codecs.open(fpath, "r", encoding="utf-8") as fin:
#         cxjson = json.loads(fin.read())
#
#     reader = CxJsonReader()
#     g = reader.read(cxjson)
#
#     fname = os.path.basename(fpath)
#     net = Network(fname)
#     net.scene.setBackgroundBrush(Qt.transparent)
#
#
# def write_cx(net, fpath):
#     with codecs.open(fpath, "w", encoding="utf-8") as fout:
#         fout.write(json.dumps(net.to_dict()))
# # end of def
