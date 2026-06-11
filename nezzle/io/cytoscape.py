"""Read and write the Cytoscape.js JSON network format (``.cyjs``).

This is the format produced by Cytoscape desktop via
``File > Export > Network to File... > Cytoscape.js JSON``. Unlike SIF it
carries node positions, so the imported layout matches what the user saw in
Cytoscape. Visual styling (colors, arrow shapes) is exported by Cytoscape to a
*separate* style file, so it is not present here — nezzle defaults are applied,
and edge ``interaction`` types can be mapped to arrow heads via ``edge_map``
exactly like the SIF importer.

Document shape (the parts we use)::

    {
      "data": { "name": "<network name>", ... },
      "elements": {
        "nodes": [ { "data": {"id": "..", "name": ".."},
                     "position": {"x": .., "y": ..} }, ... ],
        "edges": [ { "data": {"id": "..", "source": "..", "target": "..",
                              "interaction": ".."} }, ... ]
      }
    }

The reader is defensive about the wrapper: it also accepts a bare
``{"nodes": [...], "edges": [...]}`` object and the flat Cytoscape.js element
list (``[{"group": "nodes", "data": {...}}, ...]``).

Cytoscape.js uses screen coordinates (y grows downward), the same convention
as Qt's scene, so positions are used verbatim.
"""
import os
import json
import codecs
import math
import random
from collections import defaultdict

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


# Default node geometry when the file carries none (the standard Cytoscape.js
# export keeps visual properties in a separate style file).
_DEFAULT_NODE_WIDTH = 50
_DEFAULT_NODE_HEIGHT = 35

_NONE_INTERACTION = "None"


def _load_json(fpath):
    with codecs.open(fpath, "r", encoding="utf-8-sig") as fin:
        return json.loads(fin.read())


def _extract_elements(doc):
    """Return ``(nodes, edges)`` lists of element dicts from any of the
    accepted Cytoscape.js layouts."""
    if isinstance(doc, dict) and "elements" in doc:
        elements = doc["elements"]
    else:
        elements = doc

    # Flat element list: [{"group": "nodes"|"edges", "data": {...}}, ...]
    if isinstance(elements, list):
        nodes, edges = [], []
        for el in elements:
            group = el.get("group")
            if group == "nodes":
                nodes.append(el)
            elif group == "edges":
                edges.append(el)
            elif "source" in el.get("data", {}):
                edges.append(el)  # group omitted but clearly an edge
            else:
                nodes.append(el)
        return nodes, edges

    if isinstance(elements, dict):
        return elements.get("nodes", []) or [], elements.get("edges", []) or []

    raise ValueError("Unrecognized Cytoscape.js structure: no elements found.")


def _network_name(doc, fpath):
    if isinstance(doc, dict):
        data = doc.get("data")
        if isinstance(data, dict):
            for key in ("name", "shared_name", "title"):
                if data.get(key):
                    return str(data[key])
    return os.path.basename(fpath)


def _coerce_id(value):
    """Cytoscape ids are usually strings but may be numbers; normalize to str
    so node ids and the edge source/target references compare equal."""
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def _interaction_of(edge_data):
    for key in ("interaction", "shared_interaction"):
        val = edge_data.get(key)
        if val:
            return str(val)
    return _NONE_INTERACTION


def read_metadata_from_cyjs(fpath):
    doc = _load_json(fpath)
    _, edges = _extract_elements(doc)

    interactions = defaultdict(int)
    for el in edges:
        interactions[_interaction_of(el.get("data", {}))] += 1

    metadata = {}
    metadata["NETWORK_NAME"] = _network_name(doc, fpath)
    metadata["INTERACTIONS"] = interactions
    return metadata
# end of def


def read_cyjs(fpath, edge_map=None):
    doc = _load_json(fpath)
    node_elements, edge_elements = _extract_elements(doc)

    net = Network(_network_name(doc, fpath))
    net.scene.setBackgroundBrush(Qt.transparent)

    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")

    # Random fallback placement, identical in spirit to the SIF importer, for
    # nodes that have no stored position.
    half_width = DEFAULT_SCENE_WIDTH / 2
    half_height = DEFAULT_SCENE_HEIGHT / 2
    range_x = (-DEFAULT_SCENE_WIDTH / 4, DEFAULT_SCENE_WIDTH / 4)
    range_y = (-DEFAULT_SCENE_HEIGHT / 4, DEFAULT_SCENE_HEIGHT / 4)

    nodes = {}
    names = {}
    for el in node_elements:
        data = el.get("data", {})
        iden = _coerce_id(data.get("id"))
        if iden is None:
            iden = _coerce_id(data.get("SUID"))
        if iden is None or iden in nodes:
            continue

        pos = el.get("position")
        if isinstance(pos, dict) and pos.get("x") is not None \
                and pos.get("y") is not None:
            x = float(pos["x"])
            y = float(pos["y"])
        else:
            x = half_width + random.uniform(*range_x)
            y = half_height + random.uniform(*range_y)

        width = float(data.get("width", _DEFAULT_NODE_WIDTH))
        height = float(data.get("height", _DEFAULT_NODE_HEIGHT))

        node = NodeClass(iden, width=width, height=height,
                         pos=QPointF(x, y))
        node["FILL_COLOR"] = Qt.white
        node["BORDER_COLOR"] = Qt.darkGray

        # nezzle identity stays the (stable) Cytoscape id so edges resolve;
        # the human-readable name drives the display label and round-trips.
        name = str(data.get("name") or data.get("shared_name") or iden)
        node.name = name
        nodes[iden] = node
        names[iden] = name
    # end of for: nodes

    for el in edge_elements:
        data = el.get("data", {})
        str_src = _coerce_id(data.get("source"))
        str_trg = _coerce_id(data.get("target"))
        if str_src is None or str_trg is None:
            continue
        if str_src not in nodes or str_trg not in nodes:
            # Edge references a node that was not declared; skip it rather
            # than fabricate a node with no position.
            continue

        str_interaction = _interaction_of(data)
        if edge_map and (str_interaction not in edge_map):
            raise ValueError("Undefined edge type: %s" % (str_interaction))

        head = None
        if edge_map:
            ArrowClass = ArrowClassFactory.create(edge_map[str_interaction])
            if ArrowClass:
                head = ArrowClass()

        iden = _coerce_id(data.get("id")) or \
            "%s%s%s" % (str_src, str_interaction, str_trg)

        src = nodes[str_src]
        trg = nodes[str_trg]

        if str_src == str_trg:  # Self-loop edge
            EdgeClass = EdgeClassFactory.create('SELFLOOP_EDGE')
            edge = EdgeClass(iden=iden, name=str_interaction,
                             node=src, head=head)
            edge["FILL_COLOR"] = QColor(100, 100, 100, 100)
        else:
            EdgeClass = EdgeClassFactory.create('CURVED_EDGE')
            edge = EdgeClass(iden=iden, name=str_interaction,
                             source=src, target=trg, head=head)
            edge["FILL_COLOR"] = Qt.black

        src.add_edge(edge)
        trg.add_edge(edge)
        net.add_edge(edge)
    # end of for: edges

    # Add nodes and their centered labels.
    LabelClass = LabelClassFactory.create("TEXT_LABEL")
    for iden, node in nodes.items():
        net.add_node(node)
        label = LabelClass(node, names[iden])
        label["FONT_FAMILY"] = "Tahoma"
        label["FONT_SIZE"] = 10
        label.align()  # center the visible text on the node
        net.add_label(label)
    # end of for

    # Curve apart reciprocal edges so an A->B and B->A pair do not overlap,
    # matching the SIF importer's behavior.
    for src, trg, attr in net.nxgraph.edges(data=True):
        if net.nxgraph.has_edge(trg, src):
            if src == trg:  # Skip self-loops
                continue
            edge = attr['GRAPHICS']
            mid = internal_division(edge.pos_src, edge.pos_trg, 0.5, 0.5)
            d = dist(edge.pos_src, mid) / math.cos(math.pi / 4)
            cp = rotate(edge.pos_src, mid, -30, d)
            edge.ctrl_point.setPos(cp)

    return net
# end of def


def write_cyjs(net, fpath):
    """Export a nezzle network to the Cytoscape.js JSON format.

    Writes node ids, display names and positions plus edge source/target and
    interaction type — the data Cytoscape needs to reconstruct the graph and
    its layout. nezzle-specific visual styling is not emitted (Cytoscape keeps
    style in a separate file).
    """
    nodes = []
    for iden, node in net.nodes.items():
        pos = node.pos()
        nodes.append({
            "data": {"id": str(node.iden), "name": str(node.name)},
            "position": {"x": pos.x(), "y": pos.y()},
        })

    edges = []
    for iden, edge in net.edges.items():
        if 'SELFLOOP' in edge.ITEM_TYPE:
            str_src = str_trg = str(edge.node.iden)
        else:
            str_src = str(edge.source.iden)
            str_trg = str(edge.target.iden)

        edges.append({
            "data": {
                "id": str(edge.iden),
                "source": str_src,
                "target": str_trg,
                "interaction": edge.name if edge.name else "",
            }
        })

    doc = {
        "format_version": "1.0",
        "generated_by": "nezzle",
        "target_cytoscapejs_version": "~2.1",
        "data": {"name": net.name},
        "elements": {"nodes": nodes, "edges": edges},
    }

    with codecs.open(fpath, "w", encoding="utf-8") as fout:
        fout.write(json.dumps(doc, indent=2))
# end of def
