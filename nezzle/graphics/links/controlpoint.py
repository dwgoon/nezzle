from qtpy.QtWidgets import QGraphicsItem
from qtpy.QtCore import QRectF
from qtpy.QtCore import QPointF
from qtpy.QtCore import Qt
from qtpy.QtGui import QColor
from qtpy.QtGui import QPainterPath

from nezzle.graphics.baseitem import Movable
from nezzle.utils import length


class BaseControlPoint(QGraphicsItem, Movable):
    def __init__(self, parent, pos, radius=5, sticky_radius=None):
        super().__init__()
        self.setParentItem(parent)
        self._radius = radius

        if not sticky_radius:
            sticky_radius = 4 * self.parent.width

        self._sticky_radius = sticky_radius

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
    def sticky_radius(self):
        return self._sticky_radius

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

        if self.isSelected():
            painter.setPen(QColor(255, 0, 102, 200))
            painter.drawEllipse(self.rect)
            painter.setBrush(QColor(255, 0, 102, 200))
            painter.drawEllipse(self.small_rect)
        else:
            painter.setPen(QColor(100, 100, 100))
            painter.drawEllipse(self.rect)
            painter.setBrush(Qt.white)
            painter.drawEllipse(self.small_rect)

        self.scene().invalidate()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parent.setSelected(True)


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

    def mouseReleaseEvent(self, event):
        if self.parent.is_straight() or length(self.pos()) < self.sticky_radius:
           self.setPos(QPointF(0, 0))

        return super().mouseReleaseEvent(event)


class ConnectorControlPoint(BaseControlPoint):
    def __init__(self, iden, connectors=None, *args, **kwargs):
        self._iden = iden
        self._connectors = []
        if connectors:
            for obj in connectors:
                self.append_connector(obj)

        super().__init__(*args, **kwargs)

    @property
    def iden(self):
        return self._iden

    @property
    def connectors(self):
        return self._connectors

    def append_connector(self, obj):
        if len(self._connectors) == 2:
            raise ValueError("Cannot append connector. The maximum number of connectors is two.")

        if not isinstance(obj, QPointF):
            raise TypeError("Type of connector should be QPointF, not %s." % (type(obj)))

        self._connectors.append(obj)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            pos = value
            self.parent[f'CTRL_{self._iden}_POS_X'] = pos.x()
            self.parent[f'CTRL_{self._iden}_POS_Y'] = pos.y()
            self.parent.update()

        return super().itemChange(change, value)


class XaxisConnectorControlPoint(ConnectorControlPoint):
    def update_pos(self, pos):
        # Limit the range of y-axis.
        mp_y = (self.connectors[0].y() + self.connectors[1].y()) / 2  # Y-axis midpoint of connectors
        pos.setY(mp_y)

        # Control the x-coordinates of connectors.
        self.connectors[0].setX(pos.x())
        self.connectors[1].setX(pos.x())

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            if self.parent.is_node_selected():
                return super().itemChange(change, self.pos())

            pos = value
            self.update_pos(pos)
            return super().itemChange(change, value)

        elif change == QGraphicsItem.ItemPositionHasChanged:
            self.parent.update()

        return super().itemChange(change, value)

    # def mouseReleaseEvent(self, event):
    #     if length(self.pos()) < self.sticky_radius:
    #        self.setPos(QPointF(0, 0))
    #
    #     return super().mouseReleaseEvent(event)


class YaxisConnectorControlPoint(ConnectorControlPoint):
    def update_pos(self, pos):
        # Limit the range of x-axis.
        mp_x = (self.connectors[0].x() + self.connectors[1].x()) / 2  # X-axis midpoint of connectors
        pos.setX(mp_x)

        # Control the y-coordinates of connectors.
        self.connectors[0].setY(pos.y())
        self.connectors[1].setY(pos.y())

    def itemChange(self, change, value):

        if change == QGraphicsItem.ItemPositionChange:
            if self.parent.is_node_selected():
                return super().itemChange(change, self.pos())

            pos = value
            self.update_pos(pos)
            return super().itemChange(change, value)

        elif change == QGraphicsItem.ItemPositionHasChanged:
            self.parent.update()

            # if self.parent.is_header_visible():
            #     pos = value
            #     self.update_pos(pos)
            # else:
            #     self.update_pos(self.parent.pos())
            #
            # self.parent.update()
            # print("[YCP] Is header visible:",  self.parent.is_header_visible())
            # print("[YCP] %s, %s"%(self.parent.pos(), value))

        return super().itemChange(change, value)

    # def mouseReleaseEvent(self, event):
    #     if length(self.pos()) < self.sticky_radius:
    #        self.setPos(QPointF(0, 0))
    #
    #     return super().mouseReleaseEvent(event)