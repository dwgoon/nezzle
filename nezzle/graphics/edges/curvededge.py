import math
import numpy as np
from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtCore import QLineF
from qtpy.QtCore import QRectF
from qtpy.QtGui import QColor, QPainterPath, QPainterPathStroker, QPen
from qtpy.QtWidgets import QGraphicsItem
from qtpy.QtWidgets import QStyle

from nezzle.graphics.edges.straightedge import StraightEdge
from nezzle.graphics.edges.controlpoint import ControlPoint

from nezzle.utils import dot
from nezzle.utils import internal_division
from nezzle.utils import length
from nezzle.graphics import quadbezier
from nezzle.graphics.mixins import Lockable


# Reused across all curved edges — QPainterPathStroker is stateful (width/cap
# are mutated per call) but cheap to allocate; sharing avoids a per-recompute
# alloc. Width is set explicitly before each createStroke() call.
_CURVE_STROKER = QPainterPathStroker()
_CURVE_STROKER.setCapStyle(Qt.FlatCap)
_CURVE_STROKER.setJoinStyle(Qt.MiterJoin)


@Lockable
class CurvedEdge(StraightEdge):

    ITEM_TYPE = 'CURVED_EDGE'

    def __init__(self, *args, **kwargs):
        self._t_head = 0
        super().__init__(*args, **kwargs)

        self._attr.set_trigger('CP_POS_X',
                               self._trigger_set_cp_pos_x,
                               when='set')

        self._attr.set_trigger('CP_POS_Y',
                               self._trigger_set_cp_pos_y,
                               when='set')

        # (Previously kept a 50-sample _arr_t grid for the linear arc-length
        # scan. Replaced by quadbezier.find_t_for_arclen — closed-form, no
        # allocation per call.)

    @property
    def pos_ctrl(self):
        cp = self._ctrl_point
        return cp.pos() if cp is not None else self._cp_pos

    @property
    def ctrl_point(self):
        self._ensure_ctrl_point()
        return self._ctrl_point

    def _ensure_ctrl_point(self):
        # The ControlPoint child item is materialized on first need (first
        # selection or explicit ctrl_point access): constructing one per
        # edge dominated bulk network loading, and an unselected edge's
        # handle is invisible and unclickable anyway.
        if self._ctrl_point is None:
            self._ctrl_point = ControlPoint(parent=self, pos=self._cp_pos)
            self._ctrl_point.setVisible(self.isSelected()
                                        and not self.is_node_selected())

    def _trigger_set_cp_pos_x(self, key, value):
        self._cp_pos.setX(value)
        if self._ctrl_point is not None:
            self._ctrl_point.setX(value)
        else:
            self.update()
        return value

    def _trigger_set_cp_pos_y(self, key, value):
        self._cp_pos.setY(value)
        if self._ctrl_point is not None:
            self._ctrl_point.setY(value)
        else:
            self.update()
        return value

    def _cp_visible(self, edge_selected):
        cp = self._ctrl_point
        if cp is None or self.is_node_selected():
            return False
        if edge_selected or cp.isSelected():
            return True
        # Clicking the handle makes Qt's exclusive selection deselect the
        # parent edge for a moment BEFORE the handle's own press handler
        # re-selects it. Hiding the handle in that window would break its
        # mouse grab (hidden items are ungrabbed), killing the drag — so a
        # grabbed handle always stays visible.
        scene = self.scene()
        return scene is not None and scene.mouseGrabberItem() is cp

    def itemChange(self, change, value):
        # ItemSelectedHasChanged (not ItemSelectedChange): it only fires
        # after the selection actually commits, so a Lockable-rejected click
        # can never materialize or show the handle.
        if change == QGraphicsItem.ItemSelectedHasChanged:
            if value:
                self._ensure_ctrl_point()
            cp = self._ctrl_point
            if cp is not None:
                # Keep the handle out of the scene's per-frame iteration
                # unless it can actually be seen.
                cp.setVisible(self._cp_visible(bool(value)))
                cp.update()

        return super().itemChange(change, value)

    def update(self):
        self.update_ctrl_points()
        super().update()

    def update_ctrl_points(self):
        cp = self._ctrl_point
        if cp is not None:
            cp.setVisible(self._cp_visible(self.isSelected()))

    def paint(self, painter, option, widget):
        # Flattened (BaseEdge.paint + PainterOptionItem.paint inlined):
        # curved edges dominate large scenes and the super() dispatch chain
        # costs ~4% of a no-AA frame. Keep behavior in sync with those two.
        if self._geom_dirty:
            self._recompute_geometry()

        if option.state & QStyle.State_Selected:
            pen = QPen(self._pen)
            pen.setBrush(Qt.green)
            painter.setPen(pen)
            painter.setBrush(Qt.green)
        else:
            painter.setPen(self._pen)
            painter.setBrush(self._brush)

        painter.drawPath(self._path_paint)

        if self.isSelected():
            painter.setBrush(Qt.red)
            # Centered on the local origin — the midpoint of the two nodes,
            # where the control point of a straight edge also sits.
            # (drawEllipse(QPointF, rx, ry) takes the CENTER, not a corner.)
            painter.drawEllipse(QPointF(0.0, 0.0), 2.5, 2.5)
            painter.setPen(QColor(50, 50, 50, 100))

            if not self.is_node_selected():
                # Draw control lines
                painter.drawLine(self.pos_ctrl, self.pos_src)
                painter.drawLine(self.pos_ctrl, self.pos_trg)

    def is_straight(self):
        # Pure-scalar straightness test. Original implementation used
        # length() + np.arccos + 2x np.isclose per call and dominated the
        # profile at ~130 us per recompute (called twice).
        #
        # The original checked whether the angle between (pos_src - pos_ctrl)
        # and (pos_trg - pos_ctrl) is within 0.1 rad of 0 or pi. Equivalent
        # condition: |cos(angle)| > cos(0.1) ~= 0.995, i.e. cos^2 > 0.99.
        # That removes the sqrt, the acos, and the numpy calls entirely.
        pc = self.pos_ctrl
        ps = self.pos_src
        pt = self.pos_trg
        pcx = pc.x()
        pcy = pc.y()
        v1x = ps.x() - pcx
        v1y = ps.y() - pcy
        v2x = pt.x() - pcx
        v2y = pt.y() - pcy

        len_v1_sq = v1x * v1x + v1y * v1y
        len_v2_sq = v2x * v2x + v2y * v2y
        if len_v1_sq <= 1e-16 or len_v2_sq <= 1e-16:
            return True

        dot_v1v2 = v1x * v2x + v1y * v2y
        cos_sq = (dot_v1v2 * dot_v1v2) / (len_v1_sq * len_v2_sq)
        return cos_sq > 0.99   # |cos| > ~0.995  <=>  angle within 0.1 rad of {0, pi}

    def initialize(self):
        # Path construction is deferred to the first paint()/shape(); see
        # StraightEdge.initialize.
        self._identify_pos()
        self._create_control_items()
        self._create_subpoints()

    def _update_bounding_rect(self):
        super()._update_bounding_rect()

        rect_ctrl_src = QRectF(self.pos_ctrl, self.pos_src)
        rect_ctrl_trg = QRectF(self.pos_ctrl, self.pos_trg)

        rect = self._bounding_rect
        rect = rect.united(rect_ctrl_src)
        rect = rect.united(rect_ctrl_trg)
        self._bounding_rect = rect

    def _update_conservative_bbox(self):
        """Fast O(1) superset bbox: bounding box of the three control points
        plus a margin large enough to cover stroker width and arrow head.

        Mathematically guaranteed to enclose the full stroked outline + head
        because a quadratic Bezier lies inside the convex hull of its control
        polygon (well-known property), and the stroker offsets by at most
        width/2 from the curve. Used by boundingRect() to dodge the full
        path recompute when Qt only needs a visibility / clipping test
        (very common for off-screen edges in large graphs).
        """
        ps = self.pos_src
        pc = self.pos_ctrl
        pt = self.pos_trg
        psx = ps.x(); psy = ps.y()
        pcx = pc.x(); pcy = pc.y()
        ptx = pt.x(); pty = pt.y()

        minx = psx if psx < pcx else pcx
        if ptx < minx: minx = ptx
        maxx = psx if psx > pcx else pcx
        if ptx > maxx: maxx = ptx
        miny = psy if psy < pcy else pcy
        if pty < miny: miny = pty
        maxy = psy if psy > pcy else pcy
        if pty > maxy: maxy = pty

        # Direct _width/_head reads: the property/TriggerDict hops cost ~30%
        # of this per-move refresh (both mirrors are kept in sync by
        # __init__/set_width/_trigger_set_head).
        margin = self._width * 0.5 + 2.0
        head = self._head
        if head:
            # Additive bound: covers the head's along-edge reach AND its
            # lateral half-width (e.g. Hammer heads are 7x edge width wide)
            # for any head rotation, since sqrt(h^2 + (w/2)^2) <= h + w/2.
            head_reach = (head.height + head.offset
                          + 0.5 * head.width + 2.0)
            if head_reach > margin:
                margin = head_reach
        if margin < 8.0:
            margin = 8.0  # Selected-state marker ellipse around the origin
        if self._pen:
            margin += 2.0 * self._pen.width()

        self._bounding_rect = QRectF(minx - margin, miny - margin,
                                     (maxx - minx) + 2.0 * margin,
                                     (maxy - miny) + 2.0 * margin)

    def _create_control_items(self):
        self._cp_pos = internal_division(self.pos_src, self.pos_trg,
                                         0.5, 0.5)
        self._ctrl_point = None  # Materialized lazily; see _ensure_ctrl_point.

    def _create_subpoints(self):
        self.cps = 3 * [None]
        self.cps[0] = self.pos_src
        self.cps[2] = self.pos_trg

        self._qps_top = []
        self._qps_bottom = []

        self._dps_top = []
        self._dps_bottom = []

    def _identify_head(self):
        CurvedEdge._identify_head_pos(self)
        CurvedEdge._calculate_head_angle(self)
        super()._create_head_path()

    def _identify_head_pos(self):
        offset = self._calculate_head_offset()

        p1 = self.pos_src
        p2 = self.pos_trg
        pc = self.pos_ctrl

        # Closed-form arc-length inversion: 2-term Taylor around t=1 (the
        # search region) followed by one Newton step using the exact integral.
        # No loop, no numpy array alloc — replaces the previous 50-sample
        # linear scan over self._arr_t.
        t = quadbezier.find_t_for_arclen(p1, pc, p2, offset,
                                         t_min=0.5, t_max=1.0)
        self._t_head = t

        one_minus_t = 1.0 - t
        w0 = one_minus_t * one_minus_t
        w1 = 2.0 * one_minus_t * t
        w2 = t * t
        self.pos_head.setX(w0 * p1.x() + w1 * pc.x() + w2 * p2.x())
        self.pos_head.setY(w0 * p1.y() + w1 * pc.y() + w2 * p2.y())

    def _calculate_head_offset(self):
        # Scalarized: avoids numpy ufunc overhead AND avoids the global
        # np.seterr('raise') from elbowedge.py turning a benign 0/0 (when
        # ctrl coincides with trg) into a fatal FloatingPointError.
        pc = self.pos_ctrl
        pt = self.pos_trg
        vx = pc.x() - pt.x()
        vy = pc.y() - pt.y()
        len_v_sq = vx * vx + vy * vy
        if len_v_sq < 1e-18:
            return self.head.offset + self.head.height
        cos_v = vx / math.sqrt(len_v_sq)
        if cos_v > 1.0:
            cos_v = 1.0
        elif cos_v < -1.0:
            cos_v = -1.0
        radius = self.target.calculate_radius(math.acos(cos_v))
        return radius + self.head.offset + self.head.height

    def _calculate_head_angle(self):
        self._angle_head = -QLineF(self.pos_ctrl, self.pos_head).angle()
        self._head_transform.angle = self._angle_head

    def _identify_curve_points(self):
        """Resolve the curve's end-point (truncated at head base if present)
        and update head pose. Returns the QPointF where the centerline ends.

        Callers (only _create_curve_path today) have already determined the
        curve is not straight, so we skip the redundant is_straight() check
        that used to live here. (The straight case is handled by
        StraightEdge._create_path inside _create_path.)
        """
        if self.head:
            CurvedEdge._identify_head(self)
            return self.pos_head
        return self.pos_trg

    def _create_curve_path(self):
        end_pt = self._identify_curve_points()

        # Thin centerline — Qt's stroker inflates it to a width-`self.width`
        # filled outline polygon in C++.
        center = QPainterPath()
        center.moveTo(self.pos_src)
        center.quadTo(self.pos_ctrl, end_pt)

        _CURVE_STROKER.setWidth(self.width)
        body = _CURVE_STROKER.createStroke(center)
        body.setFillRule(Qt.WindingFill)

        if self.head:
            pen = self._pen
            border_visible = (pen is not None
                              and pen.style() != Qt.NoPen
                              and pen.brush().color().alpha() > 0)
            if border_visible:
                # A visible border pen would stroke the internal seam of
                # two subpaths (body end-cap and head base lines across the
                # joint), so merge into a single true outline.
                # BaseEdge._trigger_set_border_color/_line re-dirty the
                # geometry, so this decision can never go stale.
                body = body.united(self._path_head)
            else:
                # Fill-only rendering: WindingFill of the two subpaths
                # fills exactly the union region, ~28us cheaper per
                # recompute than united(), and keeps true Beziers instead
                # of united()'s flattened polygon outline.
                body.addPath(self._path_head)

        self._path_paint = body

    def _create_path(self):
        if self.is_straight():
            return StraightEdge._create_path(self)

        try:
            self._create_curve_path()
        except FloatingPointError:
            super(StraightEdge, self)._create_path()