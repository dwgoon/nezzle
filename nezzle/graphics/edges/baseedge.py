import math

from qtpy.QtCore import QPointF
from qtpy.QtCore import QRectF

from qtpy.QtGui import QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from nezzle.utils import internal_division

from nezzle.graphics.baseitem import PainterOptionItem
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics.nodes.basenode import BaseNode


class BaseEdge(PainterOptionItem):
    """
    The very base class of all edges
    """

    ITEM_TYPE = 'EDGE'

    def __init__(self,
                 iden,
                 head=None,
                 width=2,
                 *args,
                 **kwargs):

        super().__init__(iden, *args, **kwargs)

        self._pos_head = QPointF()
        self._path_paint = QPainterPath()
        self._bounding_rect = QRectF()

        # Two-level dirty tracking for lazy geometry recompute.
        #
        #   _brect_dirty: cheap conservative bounding rect needs refresh.
        #                 Used by boundingRect() — must be fast because Qt
        #                 calls it for visibility/clipping decisions even
        #                 when the edge will not be painted this frame.
        #
        #   _geom_dirty:  full path (stroker output + tight bbox) needs
        #                 refresh. Done only when paint() / shape() actually
        #                 require the polygon.
        #
        # `update()` sets both; boundingRect() clears only _brect_dirty;
        # paint()/shape() clears both. This way off-screen edges in a large
        # network never pay the stroker/head cost.
        self._brect_dirty = True
        self._geom_dirty = True

        # No ItemSendsGeometryChanges: the 2 itemChange notifications per
        # setPos() through the Python MRO were ~half the per-move cost of an
        # edge, and the only consumer was mirroring POS_X/POS_Y into _attr —
        # which GeometryChangeItem.to_dict now refreshes at serialization.
        self.setFlags(QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsFocusable)

        self._attr.set_trigger('WIDTH', self._trigger_set_width, when='set')
        self._attr.set('WIDTH', width, trigger=False)
        self._width = width

        self._attr.set_trigger('HEAD', self._trigger_set_head, when='set')
        self._attr.set('HEAD', head, trigger=False)

        self._head = head
        if head:
            self._head.parent = self

        self.initialize()

    def __str__(self):
        return 'Edge(%s)'%(self._iden)

    @property
    def width(self):
        return self._attr['WIDTH']

    @width.setter
    def width(self, val):
        self._attr['WIDTH'] = val

    def set_width(self, val, head=True):
        if head and self.head:
            self.head.set_size_from_edge(edge_width=val)

        self._width = val
        self._attr.set('WIDTH', val, trigger=False)
        self.update()

    def _trigger_set_width(self, key, value):
        self.set_width(value)
        return value

    def _trigger_set_border_color(self, key, value):
        # The painted path can depend on pen visibility (CurvedEdge merges
        # the head subpath only when the border would stroke a seam), so a
        # border change must also invalidate the cached geometry.
        ret = super()._trigger_set_border_color(key, value)
        self._geom_dirty = True
        return ret

    def _trigger_set_border_line(self, key, value):
        ret = super()._trigger_set_border_line(key, value)
        self._geom_dirty = True
        return ret

    def _trigger_set_head(self, key, value):
        self._head = value
        if self._head:
            self._head.parent = self

        self._attr.set('HEAD', value, trigger=False)
        self.update()

        return value

    @property
    def head(self):
        return self._attr['HEAD']

    @head.setter
    def head(self, obj):
        self._attr['HEAD'] = obj

    @property
    def pos_head(self):
        return self._pos_head

    """
    [Reference] https://stackoverflow.com/a/34199293
    QGraphicsItem::shape is used for object collision detection, hit tests and knowing where mouse clicks occur.
    In contrast, QGraphicsItem::boundingRect is used when drawing an object, knowing when an object is off the screen, or obscured.
    """

    def boundingRect(self):
        # Cheap conservative path: just refresh the bbox (O(constant) work
        # using the convex-hull property of the Bezier control polygon).
        # The full path is NOT computed here.
        if self._brect_dirty:
            self._update_conservative_bbox()
            self._brect_dirty = False
        return self._bounding_rect

    def shape(self):
        # Hit-testing needs the actual filled polygon, so force a full
        # recompute if dirty.
        if self._geom_dirty:
            self._recompute_geometry()
        return self._path_paint

    def _create_head_path(self):
        points = self.head.identify_points(self.pos_head,
                                             self.width,
                                             self._head_transform)
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)

        self._path_head = path

    def update(self, *args, **kwargs):
        # Cheap: reposition (O(1) midpoint math) and mark dirty.
        # Actual Bezier work happens lazily in paint(); boundingRect() uses
        # a fast conservative-superset bbox so off-screen culling is cheap.
        #
        # _identify_pos() must run eagerly here — not inside the lazy
        # _create_path() — because paint()/shape() must never mutate the
        # item position mid-render/hit-test.
        self._identify_pos()
        if not self._brect_dirty or not self._geom_dirty:
            # Re-notify whenever a consumer may have read the previous rect.
            # (Gating this on _geom_dirty alone froze off-screen edges:
            # boundingRect() clears _brect_dirty every frame, while
            # _geom_dirty stays True until a paint that may never come.)
            self.prepareGeometryChange()
        self._brect_dirty = True
        self._geom_dirty = True
        # Explicit QGraphicsItem.update: super().update would resolve to
        # MutableMapping.update (MappableItem precedes QGraphicsItem in the
        # MRO) and silently skip the repaint request.
        return QGraphicsItem.update(self, *args, **kwargs)

    def _recompute_geometry(self):
        self._create_path()
        self._update_bounding_rect()
        self._geom_dirty = False
        self._brect_dirty = False

    def _update_conservative_bbox(self):
        # Default: derive a conservative superset from whatever the current
        # _path_paint reports plus pen padding. Subclasses with explicit
        # control-polygon information override this with a faster
        # closed-form bbox that does NOT require a fresh path.
        rect = self._path_paint.boundingRect()
        if self._pen:
            pad = 2 * self._pen.width()
            rect.adjust(-pad, -pad, +pad, +pad)
        self._bounding_rect = rect

    def paint(self, painter, option, widget):
        if self._geom_dirty:
            self._recompute_geometry()
        super().paint(painter, option, widget)
        painter.drawPath(self._path_paint)

    def to_dict(self):
        attr = super().to_dict()
        if self.head:
            attr['HEAD'] = self.head.to_dict()

        return attr

    @classmethod
    def head_from_dict(cls, attr):
        if 'HEAD' in attr:
            attr_head = attr.pop('HEAD')
            if attr_head:
                ArrowClass = ArrowClassFactory.create(attr_head['ITEM_TYPE'])
                head = ArrowClass.from_dict(attr_head) if ArrowClass else None
                return head
        return None


    @classmethod
    def from_dict(cls, attr):
        raise NotImplementedError()

    def copy(self):
        return self.from_dict(self.to_dict())

    def initialize(self):
        pass

    def _identify_pos(self):
        raise NotImplementedError()

    def _create_path(self):
        raise NotImplementedError()

    def _identify_head(self):
        raise NotImplementedError()

    def is_movable(self):
        return False

    def _update_bounding_rect(self):
        rect = self._path_paint.boundingRect()
        if self._pen:
            pad = 2 * self._pen.width()
            rect.adjust(-pad, -pad, +pad, +pad)

        # The selected-state marker ellipse is drawn around the local origin
        # (radius 5 at (-2.5, -2.5)); make sure thin edges still cover it.
        self._bounding_rect = rect.united(QRectF(-8.0, -8.0, 16.0, 16.0))


class TwoNodeEdge(BaseEdge):

    ITEM_TYPE = 'TWO_NODE_EDGE'

    def __init__(self, iden, source, target, *args, **kwargs):
        self._source = source
        self._target = target
        self.source.add_edge(self)
        self.target.add_edge(self)
        super().__init__(iden, *args, **kwargs)

    def __str__(self):
        str_edge_type = ''.join([word.title() for word in self.ITEM_TYPE.split('_')])
        return "%s(%s, %s)"%(str_edge_type, self.source.name, self.target.name)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, obj: BaseNode):
        if not obj.has_edge(self):
            obj.add_edge(self)
        self._source = obj

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, obj: BaseNode):
        if not obj.has_edge(self):
            obj.add_edge(self)
        self._target = obj

    # Read-only properties
    @property
    def pos_src(self):
        """The position of source relative to its parent edge
        """
        return self._source.pos() - self.pos()

    @property
    def pos_trg(self):
        """The position of target relative to its parent edge
        """
        return self._target.pos() - self.pos()

    def is_node_selected(self):
        return self.source.isSelected() or self.target.isSelected()

    def are_nodes_close(self):
        """Decide whether the two nodes are overlapped to show the graphics of edge appropriately.
        """
        ps = self.pos_src
        pt = self.pos_trg
        vx = pt.x() - ps.x()
        vy = pt.y() - ps.y()
        len_v = math.sqrt(vx * vx + vy * vy)
        if len_v <= 1e-6:
            return True

        # Clamped to acos domain — np.arccos would yield NaN here, which the
        # global np.seterr('raise') (set in elbowedge.py) turns fatal.
        cos_v = vx / len_v
        if cos_v > 1.0:
            cos_v = 1.0
        elif cos_v < -1.0:
            cos_v = -1.0

        radius_src = self.source.calculate_radius(math.acos(cos_v))
        radius_trg = self.target.calculate_radius(math.acos(-cos_v))

        return len_v < radius_src + radius_trg

    def _identify_pos(self):
        m = internal_division(self.source.pos(), self.target.pos(), 0.5, 0.5)
        self.setPos(m)

    def to_dict(self):
        attr = super().to_dict()
        attr['ID_SOURCE'] = self.source.iden
        attr['ID_TARGET'] = self.target.iden
        return attr

    @classmethod
    def from_dict(cls, attr, source, target):
        iden = attr.pop('ID')
        width = attr.pop('WIDTH')

        obj = cls(iden, source, target, width=width)
        obj.head = cls.head_from_dict(attr)

        if 'ZVALUE' in attr:
            obj.setZValue(attr["ZVALUE"])

        attr['ID_SOURCE'] = source.iden
        attr['ID_TARGET'] = target.iden

        obj._attr.update(attr)

        return obj

    def copy(self, source=None, target=None):
        if not source:
            source = self.source

        if not target:
            target = self.target

        return self.from_dict(self.to_dict(), source, target)
