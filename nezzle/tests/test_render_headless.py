# -*- coding: utf-8 -*-
"""Render a Network scene to an offscreen QImage and verify items actually
paint and respond to changes — the full paint pipeline (dirty flags, stroker
body, arrow heads, labels) without any window.
"""
import numpy as np
import pytest
from qtpy.QtCore import QPointF, QRectF, Qt
from qtpy.QtGui import QColor, QImage, QPainter

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import LabelClassFactory
from nezzle.graphics import Network
from nezzle.graphics import NodeClassFactory


@pytest.fixture
def network(qapp):
    net = Network("NET_RENDER_TEST")
    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")

    n1 = NodeClass("N1", 30, 30, pos=QPointF(-80, 0))
    n2 = NodeClass("N2", 30, 30, pos=QPointF(80, -40))
    n3 = NodeClass("N3", 30, 30, pos=QPointF(40, 80))
    for n in (n1, n2, n3):
        n["FILL_COLOR"] = QColor(100, 150, 200)
        n["BORDER_COLOR"] = QColor(0, 0, 0)
        n["BORDER_WIDTH"] = 2
        net.add_node(n)

    Triangle = ArrowClassFactory.create("TRIANGLE")

    CurvedEdge = EdgeClassFactory.create("CURVED_EDGE")
    e1 = CurvedEdge("E1", source=n1, target=n2, width=4, head=Triangle())
    e1["FILL_COLOR"] = QColor(60, 60, 60)
    e1.ctrl_point.setPos(QPointF(0, 50))
    e1.update()
    net.add_edge(e1)

    StraightEdge = EdgeClassFactory.create("STRAIGHT_EDGE")
    e2 = StraightEdge("E2", source=n2, target=n3, width=4, head=Triangle())
    e2["FILL_COLOR"] = QColor(60, 60, 60)
    net.add_edge(e2)

    TextLabel = LabelClassFactory.create("TEXT_LABEL")
    label = TextLabel(n1, "Node-1")
    label.iden = "L1"
    label["TEXT_COLOR"] = QColor(0, 0, 0)
    label["FONT_SIZE"] = 14
    net.add_label(label)

    # Settle the lazy edge geometry once, then pin the source rect: the
    # first paint replaces conservative bounding rects with tight ones, and
    # later tests change item sizes — a per-render itemsBoundingRect() would
    # rescale the whole image and make before/after pixel counts
    # incomparable.
    _render(net.scene)
    source = net.scene.itemsBoundingRect().adjusted(-40, -40, 40, 40)

    return net, (n1, n2, n3), (e1, e2), source


def _render(scene, source=None, w=400, h=300):
    img = QImage(w, h, QImage.Format_ARGB32)
    img.fill(QColor("white"))
    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing, True)
    if source is None:
        source = scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
    scene.render(painter, QRectF(0, 0, w, h), source,
                 Qt.KeepAspectRatio)
    painter.end()
    return img


def _to_array(img):
    img = img.convertToFormat(QImage.Format_ARGB32)
    ptr = img.bits()
    ptr.setsize(img.height() * img.bytesPerLine())
    buf = np.frombuffer(ptr, np.uint8).reshape(img.height(),
                                               img.bytesPerLine())
    return buf[:, :img.width() * 4].copy()


def _n_nonwhite(arr):
    rgb = arr.reshape(arr.shape[0], -1, 4)[:, :, :3]
    return int((rgb != 255).any(axis=2).sum())


def test_scene_renders_nodes_edges_labels(network):
    net, _, _, source = network
    img = _render(net.scene, source)
    n_painted = _n_nonwhite(_to_array(img))
    # Nodes + 2 edges + label must produce a substantial number of inked
    # pixels on a 400x300 canvas.
    assert n_painted > 500


def test_moving_node_changes_render(network):
    net, (n1, _, _), _, source = network
    before = _to_array(_render(net.scene, source))
    n1.setPos(QPointF(-80, 60))  # dirty flags must propagate to the paint
    after = _to_array(_render(net.scene, source))
    assert (before != after).any()


def test_render_is_deterministic(network):
    net, _, _, source = network
    a = _to_array(_render(net.scene, source))
    b = _to_array(_render(net.scene, source))
    assert (a == b).all()


def test_edge_width_change_repaints_thicker(network):
    net, _, (e1, e2), source = network
    before = _n_nonwhite(_to_array(_render(net.scene, source)))
    e1["WIDTH"] = 12
    e2["WIDTH"] = 12
    after = _n_nonwhite(_to_array(_render(net.scene, source)))
    assert after > before
