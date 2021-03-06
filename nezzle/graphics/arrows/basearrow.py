from qtpy.QtCore import QPointF
from nezzle.utils import TriggerDict


class BaseArrow(object):

    ITEM_TYPE = 'BASE_HEAD'

    DEFAULT_OFFSET = 4

    def __init__(self, width, height, offset):

        self._attr = TriggerDict()
        self._attr['ITEM_TYPE'] = self.ITEM_TYPE

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
        if not hasattr(self, "_parent") or not self._parent:
            raise ValueError("A edge should be assigned for this arrow before setting offset.")

        self._attr['OFFSET'] = val
        self.update()

    def _trigger_set_offset(self, key, value):
        self._offset = value
        return value

    def update(self):
        self.parent.update()

    def identify_points(self, head, edge_body_width, angle=None):
        raise NotImplementedError("identify_pos should be implemented!")

    def to_dict(self):
        dict_head = {}
        dict_head['ITEM_TYPE'] = self.ITEM_TYPE
        dict_head['WIDTH'] = self.width
        dict_head['HEIGHT'] = self.height
        dict_head['OFFSET'] = self.offset
        dict_head.update(self._attr)

        return dict_head

    @classmethod
    def from_dict(cls, dict_head):
        width = dict_head['WIDTH']
        height = dict_head['HEIGHT']
        offset = dict_head['OFFSET']
        return cls(width, height, offset=offset)


class Triangle(BaseArrow):

    ITEM_TYPE = "TRIANGLE"

    DEFAULT_WIDTH = 10
    DEFAULT_HEIGHT = 10
    DEFAULT_OFFSET = 4

    def __init__(self, width=None, height=None, offset=None, *args, **kwargs):
        if not width:
            width = Triangle.DEFAULT_WIDTH

        if not height:
            height = Triangle.DEFAULT_HEIGHT

        if not offset:
            offset = Triangle.DEFAULT_OFFSET

        super().__init__(width, height, offset, *args, **kwargs)

    def identify_points(self, head, edge_body_width, transform=None):

        neck1 = head + QPointF(0, -edge_body_width/2)
        neck2 = head + QPointF(0, +edge_body_width/2)

        face1 = head + QPointF(0.0, -self.width/2)
        face2 = head + QPointF(0.0, +self.width/2)
        top = head + QPointF(self.height, 0)

        points = [neck1, face1, top, face2, neck2]

        # transform is a callable object, which defines its own transformation in __call__.
        if transform:
            for i, pt in enumerate(points):
                points[i] = transform(pt, head)

        return points
    # end of def identify_pos

    def set_size_from_edge(self, edge_width):
        self.width = 5*edge_width
        self.height = 5*edge_width
        self.parent.update()


class Hammer(BaseArrow):

    ITEM_TYPE = "HAMMER"

    DEFAULT_WIDTH = 14
    DEFAULT_HEIGHT = 2
    DEFAULT_OFFSET = 4

    def __init__(self, width=None, height=None, offset=None, *args, **kwargs):
        if not width:
            width = Hammer.DEFAULT_WIDTH

        if not height:
            height = Hammer.DEFAULT_HEIGHT

        if not offset:
            offset = Hammer.DEFAULT_OFFSET

        super().__init__(width, height, offset, *args, **kwargs)

    def identify_points(self, head, edge_body_width, transform=None):

        neck1 = head + QPointF(0, -edge_body_width/2)
        neck2 = head + QPointF(0, +edge_body_width/2)

        face1 = head + QPointF(0, -self.width/2)
        face2 = head + QPointF(self.height, -self.width/2)

        face3 = head + QPointF(self.height, +self.width/2)
        face4 = head + QPointF(0, +self.width/2)

        points = [neck1, face1, face2, face3, face4, neck2]

        if transform:
            for i, pt in enumerate(points):
                points[i] = transform(pt, head)

        return points
    # end of def identify_pos

    def set_size_from_edge(self, edge_width):
        self.width = 7*edge_width
        self.height = edge_width
        self.parent.update()