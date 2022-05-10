import numpy as np

from qtpy.QtCore import QPointF, Qt
from qtpy.QtCore import QRectF

from qtpy.QtGui import QPainterPath
from qtpy.QtWidgets import QGraphicsItem

from nezzle.utils import dist
from nezzle.utils import length
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

        self.setFlags(QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsFocusable
                      | QGraphicsItem.ItemSendsGeometryChanges)

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            """
            The following check prevents this item being selected
            simply according to boundingRect.
            """

            pos = event.pos() - self.pos()
            if self._path_paint.contains(pos):
                self.setSelected(True)
                event.accept()
        else:
            event.reject()


    """
    [Reference] https://stackoverflow.com/a/34199293
    QGraphicsItem::shape is used for object collision detection, hit tests and knowing where mouse clicks occur.
    In contrast, QGraphicsItem::boundingRect is used when drawing an object, knowing when an object is off the screen, or obscured.
    """

    def boundingRect(self):
        return self._bounding_rect

    def shape(self):
        return self._path_paint

    def itemChange(self, change, value):
        return super().itemChange(change, value)

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
        self._create_path()
        self._update_bounding_rect()
        self._invalidate()
        return super().update(*args, **kwargs)

    def paint(self, painter, option, widget):
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

        self._bounding_rect = rect


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

    def __eq__(self, other):
        return id(other) == id(self)

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
        v = self.pos_tgt - self.pos_src
        len_v = length(v)
        if len_v <= 1e-6:
            return True

        angle_rad = np.arccos(v.x() / len_v)
        radius_src = self.source.calculate_radius(angle_rad)

        v *= -1
        angle_rad = np.arccos(v.x() / len_v)
        radius_tgt = self.target.calculate_radius(angle_rad)

        return dist(self.pos_src, self.pos_tgt) < radius_src + radius_tgt

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
