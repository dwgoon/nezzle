import math
from qtpy.QtGui import QPainterPath

from nezzle.graphics.mixins import Lockable
from nezzle.graphics.nodes.basenode import BaseNode


@Lockable
class RectangleNode(BaseNode):

    ITEM_TYPE = 'RECTANGLE_NODE'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # end of def __init__

    def shape(self):
        path = QPainterPath()
        path.addRect(self._brect)
        return path

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.drawRect(self._brect)

    def calculate_radius(self, angle):
        """
        The angle should be in radians.
        """
        a = self.width/2
        b = self.height/2
        return 1/math.sqrt(1/b**2 + (1/a**2 - 1/b**2)*(math.cos(angle)**2))


@Lockable
class SquareNode(RectangleNode):

    ITEM_TYPE = 'SQUARE_NODE'

    def __init__(self, iden, radius, *args, **kwargs):
        super().__init__(iden, width=2*radius, height=2*radius, *args, **kwargs)
        self._attr.set_trigger('RADIUS', self._trigger_set_radius)
        self._attr['RADIUS'] = radius
        assert self.width == self.height
    # end of def __init__

    def _trigger_set_radius(self, key, value):
        diameter = 2*value
        self._attr['WIDTH'] = diameter
        self._attr['HEIGHT'] = diameter
        return value

    @property
    def width(self):
        return self._attr['WIDTH']

    @width.setter
    def width(self, val):
        self._attr['RADIUS'] = val/2

    @property
    def height(self):
        return self._attr['HEIGHT']

    @height.setter
    def height(self, val):
        self._attr['RADIUS'] = val/2

    @property
    def radius(self):
        return self._attr['RADIUS']

    @radius.setter
    def radius(self, val):
        self._attr['RADIUS'] = val

    def calculate_radius(self, angle=None):
        return self.radius

    @classmethod
    def from_dict(cls, attr):
        iden = attr.pop('ID')
        radius = attr.pop('RADIUS')

        obj = cls(iden=iden, radius=radius)
        obj._attr.update(attr)

        return obj
