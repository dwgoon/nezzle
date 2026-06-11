from qtpy.QtCore import QPointF


class BaseArrow(object):
    """Plain (width, height, offset) value holder for an edge's arrow head.

    Deliberately NOT TriggerDict-backed: one arrow is constructed per edge,
    so building trigger machinery here measurably slowed bulk network
    loading while nothing ever read the attribute dict.
    """

    ITEM_TYPE = 'BASE_HEAD'

    DEFAULT_OFFSET = 4

    def __init__(self, width, height, offset):
        self._offset = offset
        self._height = height
        self._width = width

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
        self._width = val
        self.update()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, val):
        self._height = val
        self.update()

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, val):
        if not hasattr(self, "_parent") or not self._parent:
            raise ValueError("A edge should be assigned for this arrow before setting offset.")

        self._offset = val
        self.update()

    def update(self):
        self.parent.update()

    def identify_points(self, head, edge_body_width, angle=None):
        raise NotImplementedError("identify_pos should be implemented!")

    def to_dict(self):
        return {
            'ITEM_TYPE': self.ITEM_TYPE,
            'WIDTH': self._width,
            'HEIGHT': self._height,
            'OFFSET': self._offset,
        }

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