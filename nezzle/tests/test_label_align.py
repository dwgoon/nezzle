# -*- coding: utf-8 -*-
"""Headless tests for TextLabel.align().

Alignment is computed against the *visible* text ink (QFontMetricsF tight
bounds), not the loose QGraphicsTextItem.boundingRect() — the loose box pads
the text with the document margin and the font's empty descent region, which
pushes the glyphs off the node center. These tests pin the centering contract
and the relative ordering of the nine alignment modes using deterministic
font metrics (no rasterization, which is unreliable on the offscreen
platform).
"""
import pytest
from qtpy.QtCore import QPointF
from qtpy.QtGui import QFontMetricsF

from nezzle.graphics import EllipseNode, TextLabel


def _make_label(text="0", size=20):
    node = EllipseNode(text, 40, 40, pos=QPointF(0, 0))
    label = TextLabel(node, text)
    label["FONT_SIZE"] = size
    return label


def _expected_ink_rect(label):
    """Recompute the visible-ink rect independently of TextLabel._ink_rect,
    so the test cross-checks the implementation rather than mirroring it."""
    ti = label._text_item
    fm = QFontMetricsF(ti.font())
    tight = fm.tightBoundingRect(ti.toPlainText())
    margin = ti.document().documentMargin()
    baseline = margin + fm.ascent()
    left = margin + tight.left()
    top = baseline + tight.top()
    return left, top, left + tight.width(), top + tight.height()


class TestMiddleCenter:
    @pytest.mark.parametrize("text", ["0", "5", "88", "A", "g"])
    def test_ink_center_lands_on_node_origin(self, qapp, text):
        label = _make_label(text)
        label.align("middle-center")

        left, top, right, bottom = _expected_ink_rect(label)
        ink_cx = (left + right) / 2
        ink_cy = (top + bottom) / 2

        # POS places the text item's local frame; the ink center must map to
        # the node origin (0, 0).
        assert label["POS_X"] + ink_cx == pytest.approx(0.0, abs=1e-6)
        assert label["POS_Y"] + ink_cy == pytest.approx(0.0, abs=1e-6)

    def test_default_mode_is_middle_center(self, qapp):
        a = _make_label("0")
        a.align()
        b = _make_label("0")
        b.align("middle-center")
        assert a["POS_X"] == pytest.approx(b["POS_X"])
        assert a["POS_Y"] == pytest.approx(b["POS_Y"])

    def test_ink_centering_differs_from_loose_box_when_asymmetric(self, qapp):
        # Real Arial is narrower than its loose layout box (document margin +
        # advance), so loose-box centering sits the glyph left of center.
        # Ink centering must put the ink center exactly on the origin; the
        # loose-box center generally does not.
        label = _make_label("0")
        br = label._text_item.boundingRect()
        loose_pos_x = -br.width() / 2

        label.align("middle-center")
        left, _, right, _ = _expected_ink_rect(label)
        ink_cx = (left + right) / 2

        assert label["POS_X"] + ink_cx == pytest.approx(0.0, abs=1e-6)
        # The loose box would have left a residual horizontal offset.
        loose_residual = abs(loose_pos_x + ink_cx)
        ink_residual = abs(label["POS_X"] + ink_cx)
        assert ink_residual <= loose_residual + 1e-9


class TestAlignmentModesOrdering:
    def test_vertical_modes_ordered(self, qapp):
        def pos_y(mode):
            lb = _make_label("0")
            lb.align(mode)
            return lb["POS_Y"]

        # "top" places the label above the node (most negative POS_Y),
        # "bottom" below it.
        assert pos_y("top-center") < pos_y("middle-center") < pos_y("bottom-center")

    def test_horizontal_modes_ordered(self, qapp):
        def pos_x(mode):
            lb = _make_label("0")
            lb.align(mode)
            return lb["POS_X"]

        assert pos_x("middle-left") < pos_x("middle-center") < pos_x("middle-right")

    def test_top_bottom_span_matches_ink_height(self, qapp):
        lb_top = _make_label("0")
        lb_top.align("top-center")
        lb_bottom = _make_label("0")
        lb_bottom.align("bottom-center")

        left, top, right, bottom = _expected_ink_rect(lb_top)
        ink_height = bottom - top
        # Moving from bottom-aligned to top-aligned shifts the label up by
        # exactly the ink height.
        assert lb_bottom["POS_Y"] - lb_top["POS_Y"] == pytest.approx(ink_height,
                                                                     abs=1e-6)


class TestMultilineFallback:
    def test_multiline_uses_loose_box_without_error(self, qapp):
        lb = _make_label("ab\ncd")
        lb.align("middle-center")  # must not raise
        br = lb._text_item.boundingRect()
        assert lb["POS_X"] == pytest.approx(-br.width() / 2)
        assert lb["POS_Y"] == pytest.approx(-br.height() / 2)

    def test_empty_text_uses_loose_box(self, qapp):
        lb = _make_label("")
        lb.align("middle-center")  # must not raise
        br = lb._text_item.boundingRect()
        assert lb["POS_X"] == pytest.approx(-br.width() / 2)
        assert lb["POS_Y"] == pytest.approx(-br.height() / 2)
