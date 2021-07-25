from qtpy.QtWidgets import QGraphicsItem
from qtpy.QtCore import QRectF
from qtpy.QtCore import QPointF
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtGui import QPainterPath

from nezzle.graphics.baseitem import Movable
from nezzle.utils import length


class BaseControlPoint(QGraphicsItem, Movable):
    def __init__(self, parent, pos, radius=5):
        super().__init__()
        self.setParentItem(parent)
        self._radius = radius

        self.rect = QRectF(-self._radius, -self._radius,
                           2*self._radius, 2*self._radius)
        self.path = QPainterPath()
        self.path.addEllipse(self.rect)

        radius_sf = 0.7*self._radius
        self.small_rect = QRectF(-radius_sf, -radius_sf,
                                 2 * radius_sf, 2 * radius_sf)

        self.setPos(pos)

        self.setFlags(QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsMovable
                      | QGraphicsItem.ItemIsFocusable
                      | QGraphicsItem.ItemSendsGeometryChanges)

        self.ctrl_pos = None
        self.update()

    @property
    def radius(self):
        return self._radius

    @property
    def parent(self):
        return self.parentItem()


    def boundingRect(self):
        rect = QRectF()
        if not self.parent.isSelected():
            return rect

        rect = rect.united(self.rect)
        return rect

    def shape(self):
        path = QPainterPath()
        if not self.parent.isSelected():
            return path

        path.addPath(self.path)

        return path

    def paint(self, painter, option, widget):

        if not self.parent.isSelected():
            return

        painter.setPen(QColor(100, 100, 100))
        painter.drawEllipse(self.rect)
        painter.setBrush(Qt.white)
        painter.drawEllipse(self.small_rect)

        self.scene().invalidate()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parent.setSelected(True)

    def mouseReleaseEvent(self, event):
        if self.parent.is_straight() or length(self.pos())<10:
           self.setPos(QPointF(0, 0))

        return super().mouseReleaseEvent(event)


class ControlPoint(BaseControlPoint):

    def itemChange(self, change, value):

        if change == QGraphicsItem.ItemPositionChange:
            if self.parent.is_node_selected():
                return super().itemChange(change, self.pos())

        elif change == QGraphicsItem.ItemPositionHasChanged:
            pos = value
            self.parent['CTRL_POS_X'] = pos.x()
            self.parent['CTRL_POS_Y'] = pos.y()
            self.parent.update()

        return super().itemChange(change, value)


class XaxisControlPoint(BaseControlPoint):

    def itemChange(self, change, value):

        if change == QGraphicsItem.ItemPositionChange:
            if self.parent.is_node_selected():
                return super().itemChange(change, self.pos())

            pos = value
            pos.setY(0)  # Limit the range of y-axis

        elif change == QGraphicsItem.ItemPositionHasChanged:
            pos = value
            self.parent['CTRL_POS_X'] = pos.x()
            self.parent['CTRL_POS_Y'] = pos.y()
            self.parent.update()

        return super().itemChange(change, value)

