# -*- coding: utf-8 -*-

from qtpy.QtCore import QPointF
from nezzle.utils import rotate
from nezzle.utils import TriggerDict

class HeaderClassFactory(object):
    @staticmethod
    def create(header_type):
        if header_type.upper() == 'ARROW':
            return Arrow
        elif header_type.upper() == 'HAMMER':
            return Hammer
        else:
            raise TypeError("Undefined lins type: %s" % (header_type))


class BaseHeader(object):

    TYPE = 'BASE_HEADER'

    def __init__(self, width, height, offset=4):

        self._attr = TriggerDict()
        self._attr['TYPE'] = self.TYPE

        self._offset = offset
        self._height = height
        self._width = width

        self._attr.set_trigger('WIDTH', self._trigger_set_width, when='set')
        self._attr.set_trigger('HEIGHT', self._trigger_set_height, when='set')
        self._attr.set_trigger('OFFSET', self._trigger_set_offset, when='set')
        
        self._attr['WIDTH'] = width
        self._attr['HEIGHT'] = height
        self._attr['OFFSET'] = offset

    # Read-write properties
    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, obj):
        self._parent = obj

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._attr['WIDTH'] = val
        self.update()

    def _trigger_set_width(self, key, value):
        self._width = value
        return value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        self._attr['HEIGHT'] = val
        self.update()

    def _trigger_set_height(self, key, value):
        self._height = value
        return value

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, val):
        self._attr['OFFSET'] = val
        self.update()

    def _trigger_set_offset(self, key, value):
        self._offset = value
        return value

    # @property
    # def symbol(self):
    #     return self._symbol
    #
    # @symbol.setter
    # def symbol(self, val):
    #     self._symbol = val

    def update(self):
        self.parent.update()

    def calculate_points(self, head, link_body_width, angle=None):
        raise NotImplementedError("calculate_points should be implemented!")

    def to_dict(self):
        dict_header = {}
        dict_header['TYPE'] = self.TYPE
        dict_header['WIDTH'] = self.width
        dict_header['HEIGHT'] = self.height
        dict_header['OFFSET'] = self.offset
        dict_header.update(self._attr)

        return dict_header

    @classmethod
    def from_dict(cls, dict_header):
        width = dict_header['WIDTH']
        height = dict_header['HEIGHT']
        offset = dict_header['OFFSET']
        header_type = dict_header['TYPE']
        HeaderClass = HeaderClassFactory.create(header_type)
        return HeaderClass(width, height,
                           offset=offset)


class Arrow(BaseHeader):

    TYPE = 'ARROW'

    def __init__(self, width=10, height=10, *args, **kwargs):
        super().__init__(width, height, *args, **kwargs)

    def calculate_points(self, head, link_body_width, angle=None):

        neck1 = head + QPointF(0, -link_body_width/2)
        neck2 = head + QPointF(0, +link_body_width/2)

        face1 = head + QPointF(0.0, -self.width/2)
        face2 = head + QPointF(0.0, +self.width/2)
        top = head + QPointF(self.height, 0)

        points = [neck1, face1, top, face2, neck2]
        if angle:
            for i, pt in enumerate(points):
                points[i] = rotate(head, pt, angle)

        return points
    # end of def calculate_points

    def set_size_from_link(self, link_width):
        self.width = 5*link_width
        self.height = 5*link_width
        self.parent.update()


class Hammer(BaseHeader):

    TYPE = 'HAMMER'

    def __init__(self, width=14, height=2, *args, **kwargs):
        super().__init__(width, height, *args, **kwargs)

    def calculate_points(self, head, link_body_width, angle=None):

        neck1 = head + QPointF(0, -link_body_width/2)
        neck2 = head + QPointF(0, +link_body_width/2)

        face1 = head + QPointF(0, -self.width/2)
        face2 = head + QPointF(self.height, -self.width/2)

        face3 = head + QPointF(self.height, +self.width/2)
        face4 = head + QPointF(0, +self.width/2)

        points = [neck1, face1, face2, face3, face4, neck2]

        if angle:
            for i, pt in enumerate(points):
                points[i] = rotate(head, pt, angle)

        return points
    # end of def calculate_points

    def set_size_from_link(self, link_width):
        self.width = 7*link_width
        self.height = link_width
        self.parent.update()