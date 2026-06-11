# -*- coding: utf-8 -*-
"""Headless tests for the edge geometry pipeline: lazy dirty-flag recompute,
conservative bounding boxes, head placement on the curve, and the straight
path polygon.
"""
import math

import pytest
from qtpy.QtCore import QPointF

from nezzle.graphics import ArrowClassFactory
from nezzle.graphics import EdgeClassFactory
from nezzle.graphics import NodeClassFactory


def _make_nodes(src_pos, trg_pos):
    NodeClass = NodeClassFactory.create("ELLIPSE_NODE")
    n1 = NodeClass("N1", 30, 30, pos=src_pos)
    n2 = NodeClass("N2", 30, 30, pos=trg_pos)
    return n1, n2


def _make_curved(src_pos=QPointF(0, 0), trg_pos=QPointF(200, 0), width=3,
                 with_head=True, ctrl_local=QPointF(0, 60)):
    n1, n2 = _make_nodes(src_pos, trg_pos)
    head = ArrowClassFactory.create("TRIANGLE")() if with_head else None
    EdgeClass = EdgeClassFactory.create("CURVED_EDGE")
    edge = EdgeClass("E1", source=n1, target=n2, width=width, head=head)
    if ctrl_local is not None:
        # Local coords: the edge sits at the chord midpoint, so (0, dy)
        # bends the curve perpendicular to the chord.
        edge.ctrl_point.setPos(ctrl_local)
        edge.update()
    return n1, n2, edge


def _bezier_point(p1, pc, p2, t):
    w0 = (1.0 - t) * (1.0 - t)
    w1 = 2.0 * t * (1.0 - t)
    w2 = t * t
    return (w0 * p1.x() + w1 * pc.x() + w2 * p2.x(),
            w0 * p1.y() + w1 * pc.y() + w2 * p2.y())


class TestDirtyFlags:
    def test_shape_clears_dirty(self, qapp):
        _, _, edge = _make_curved()
        edge._geom_dirty = True
        edge.shape()
        assert not edge._geom_dirty
        assert not edge._brect_dirty

    def test_node_move_marks_dirty(self, qapp):
        n1, _, edge = _make_curved()
        edge.shape()  # clean state
        n1.setPos(QPointF(10, 5))
        assert edge._geom_dirty
        assert edge._brect_dirty

    def test_bounding_rect_while_dirty_keeps_geometry_lazy(self, qapp):
        n1, _, edge = _make_curved()
        edge.shape()
        n1.setPos(QPointF(25, -10))
        rect = edge.boundingRect()
        assert rect.isValid()
        # boundingRect() must not pay for the full path recompute.
        assert edge._geom_dirty
        assert not edge._brect_dirty

    def test_ctrl_point_move_marks_dirty(self, qapp):
        _, _, edge = _make_curved()
        edge.shape()
        edge.ctrl_point.setPos(QPointF(5, 80))
        assert edge._geom_dirty


class TestConservativeBoundingBox:
    @pytest.mark.parametrize("edge_type", ["CURVED_EDGE", "STRAIGHT_EDGE"])
    @pytest.mark.parametrize("with_head", [True, False])
    def test_contains_tight_path_rect(self, qapp, edge_type, with_head):
        n1, n2 = _make_nodes(QPointF(0, 0), QPointF(173, 91))
        head = ArrowClassFactory.create("TRIANGLE")() if with_head else None
        EdgeClass = EdgeClassFactory.create(edge_type)
        edge = EdgeClass("E1", source=n1, target=n2, width=4, head=head)
        if edge_type == "CURVED_EDGE":
            edge.ctrl_point.setPos(QPointF(20, 70))
            edge.update()

        n1.setPos(QPointF(-31, 17))  # dirty everything
        conservative = edge.boundingRect()

        edge._recompute_geometry()
        tight = edge._path_paint.boundingRect()

        assert conservative.contains(tight)


class TestHeadPlacement:
    def test_head_lies_on_bezier_curve(self, qapp):
        _, _, edge = _make_curved(ctrl_local=QPointF(0, 60))
        edge.shape()  # force geometry

        assert not edge.is_straight()
        t = edge._t_head
        assert 0.5 <= t <= 1.0

        bx, by = _bezier_point(edge.pos_src, edge.ctrl_point.pos(),
                               edge.pos_trg, t)
        assert edge.pos_head.x() == pytest.approx(bx, abs=1e-6)
        assert edge.pos_head.y() == pytest.approx(by, abs=1e-6)

    def test_head_offset_keeps_head_outside_target(self, qapp):
        _, n2, edge = _make_curved(ctrl_local=QPointF(0, 60))
        edge.shape()
        # The head base is pushed back from the target center by at least
        # the node radius (15) plus arrow offset+height.
        d = math.hypot(edge.pos_head.x() - edge.pos_trg.x(),
                       edge.pos_head.y() - edge.pos_trg.y())
        assert d >= 15.0

    def test_set_width_resizes_head(self, qapp):
        _, _, edge = _make_curved(width=3)
        edge["WIDTH"] = 6
        assert edge.width == 6
        # Triangle.set_size_from_edge: width = height = 5 * edge width
        assert edge.head.width == 30
        assert edge.head.height == 30


class TestIsStraight:
    def test_ctrl_near_chord_is_straight(self, qapp):
        _, _, edge = _make_curved(ctrl_local=QPointF(0, 0.2))
        assert edge.is_straight()

    def test_ctrl_off_chord_is_curved(self, qapp):
        _, _, edge = _make_curved(ctrl_local=QPointF(0, 50))
        assert not edge.is_straight()

    def test_straight_edge_falls_back_to_straight_path(self, qapp):
        # A curved edge whose ctrl point sits on the chord must paint as a
        # plain straight edge without raising.
        _, _, edge = _make_curved(ctrl_local=QPointF(0, 0.0))
        edge._geom_dirty = True
        edge._recompute_geometry()
        assert not edge._path_paint.isEmpty()


class TestStraightEdgePath:
    def test_headless_path_is_expected_rectangle(self, qapp):
        n1, n2 = _make_nodes(QPointF(0, 0), QPointF(100, 0))
        EdgeClass = EdgeClassFactory.create("STRAIGHT_EDGE")
        edge = EdgeClass("E1", source=n1, target=n2, width=4, head=None)
        edge._geom_dirty = True
        edge._recompute_geometry()

        # Local coords: edge sits at the chord midpoint (50, 0), so the
        # stroke rectangle spans (-50..50) x (-2..2).
        polygons = edge._path_paint.toSubpathPolygons()
        assert len(polygons) == 1
        points = {(round(p.x(), 6), round(p.y(), 6)) for p in polygons[0]}
        expected = {(-50.0, -2.0), (-50.0, 2.0), (50.0, -2.0), (50.0, 2.0)}
        assert expected <= points

    def test_with_head_path_is_nonempty_and_contains_head(self, qapp):
        n1, n2 = _make_nodes(QPointF(0, 0), QPointF(100, 0))
        head = ArrowClassFactory.create("TRIANGLE")()
        EdgeClass = EdgeClassFactory.create("STRAIGHT_EDGE")
        edge = EdgeClass("E1", source=n1, target=n2, width=4, head=head)
        edge._geom_dirty = True
        edge._recompute_geometry()
        assert not edge._path_paint.isEmpty()
        # Head base must sit between the chord midpoint and the target.
        assert 0.0 < edge.pos_head.x() < 50.0


class TestOtherEdgeTypesSmoke:
    @pytest.mark.parametrize("edge_type", [
        "VERTICAL_ELBOW_EDGE",
        "HORIZONTAL_ELBOW_EDGE",
    ])
    def test_construct_and_compute_geometry(self, qapp, edge_type):
        n1, n2 = _make_nodes(QPointF(0, 0), QPointF(150, 90))
        head = ArrowClassFactory.create("TRIANGLE")()
        EdgeClass = EdgeClassFactory.create(edge_type)
        edge = EdgeClass("E1", source=n1, target=n2, width=3, head=head)
        assert not edge.shape().isEmpty()
        assert edge.boundingRect().isValid()
