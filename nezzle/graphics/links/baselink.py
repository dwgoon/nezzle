import numpy as np

from qtpy.QtCore import QPoint, QPointF, Qt
from qtpy.QtCore import QRectF
from qtpy.QtCore import QLineF

from qtpy.QtGui import QTransform
from qtpy.QtGui import QColor, QPainterPath, QPainter
from qtpy.QtGui import QPolygonF
from qtpy.QtGui import QPen
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView
from qtpy.QtWidgets import QGraphicsItem

from nezzle.utils import dist
from nezzle.utils import dot
from nezzle.utils import length
from nezzle.utils import internal_division
from nezzle.utils import rotate
from nezzle.graphics import quadbezier
from nezzle.graphics.mixins import Lockable
from nezzle.graphics.baseitem import PainterOptionItem
from nezzle.graphics import ArrowClassFactory
from nezzle.graphics.nodes.basenode import BaseNode


class BaseLink(PainterOptionItem):
    __doc__ = r"""
       [`TwoNodeLink`][nezzle.graphics.links.baselink.TwoNodeLink]
       Applies a 2D convolution over an input signal composed of several input
       planes.
       In the simplest case, the output value of the layer with input size
       $`(N, C_{\text{in}}, H, W)`$ 
       and output $`(N, C_{\text{out}}, H_{\text{out}}, W_{\text{out}})`$ 
       can be precisely described as:
       
       ```math
           \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
           \sum_{k = 0}^{C_{\text{in}} - 1} \text{weight}(C_{\text{out}_j}, k) \star \text{input}(N_i, k)
           
       ```
       where $`\star`$ is the valid 2D `cross-correlation`_ operator,
       ```math
       `N` is a batch size, `C` denotes a number of channels,
       `H` is a height of input planes in pixels, and `W` is
       width in pixels.
       ```

       This module supports `TensorFloat32<tf32_on_ampere>`.
       * ``stride`` controls the stride for the cross-correlation, a single
         number or a tuple.
       * :attr:`padding` controls the amount of padding applied to the input. It
         can be either a string {{'valid', 'same'}} or a tuple of ints giving the
         amount of implicit padding applied on both sides.
       * :attr:`dilation` controls the spacing between the kernel points; also
         known as the à trous algorithm. It is harder to describe, but this `link`_
         has a nice visualization of what :attr:`dilation` does.
       {groups_note}
       The parameters ``kernel_size``, `stride`, :attr:`padding`, :attr:`dilation` can either be:
           - a single ``int`` -- in which case the same value is used for the height and width dimension
           - a ``tuple`` of two ints -- in which case, the first `int` is used for the height dimension,
             and the second `int` for the width dimension
       Note:
           {depthwise_separable_note}
       Note:
           {cudnn_reproducibility_note}
       Note:
           ``padding='valid'`` is the same as no padding. ``padding='same'`` pads
           the input so the output has the shape as the input. However, this mode
           doesn't support any stride values other than 1.
       Args:
           in_channels (int): Number of channels in the input image
           out_channels (int): Number of channels produced by the convolution
           kernel_size (int or tuple): Size of the convolving kernel
           stride (int or tuple, optional): Stride of the convolution. Default: 1
           padding (int, tuple or str, optional): Padding added to all four sides of
               the input. Default: 0
           padding_mode (string, optional): ``'zeros'``, ``'reflect'``,
               ``'replicate'`` or ``'circular'``. Default: ``'zeros'``
           dilation (int or tuple, optional): Spacing between kernel elements. Default: 1
           groups (int, optional): Number of blocked connections from input
               channels to output channels. Default: 1
           bias (bool, optional): If ``True``, adds a learnable bias to the
               output. Default: ``True``
       """  + r"""
       Shape:
           - Input: :math:`(N, C_{in}, H_{in}, W_{in})`
           - Output: :math:`(N, C_{out}, H_{out}, W_{out})` where
             .. math::
                 H_{out} = \left\lfloor\frac{H_{in}  + 2 \times \text{padding}[0] - \text{dilation}[0]
                           \times (\text{kernel\_size}[0] - 1) - 1}{\text{stride}[0]} + 1\right\rfloor
             .. math::
                 W_{out} = \left\lfloor\frac{W_{in}  + 2 \times \text{padding}[1] - \text{dilation}[1]
                           \times (\text{kernel\_size}[1] - 1) - 1}{\text{stride}[1]} + 1\right\rfloor
       Attributes:
           weight (Tensor): the learnable weights of the module of shape
               :math:`(\text{out\_channels}, \frac{\text{in\_channels}}{\text{groups}},`
               :math:`\text{kernel\_size[0]}, \text{kernel\_size[1]})`.
               The values of these weights are sampled from
               :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
               :math:`k = \frac{groups}{C_\text{in} * \prod_{i=0}^{1}\text{kernel\_size}[i]}`
           bias (Tensor):   the learnable bias of the module of shape
               (out_channels). If :attr:`bias` is ``True``,
               then the values of these weights are
               sampled from :math:`\mathcal{U}(-\sqrt{k}, \sqrt{k})` where
               :math:`k = \frac{groups}{C_\text{in} * \prod_{i=0}^{1}\text{kernel\_size}[i]}`
       Examples:
           >>> # With square kernels and equal stride
           >>> m = nn.Conv2d(16, 33, 3, stride=2)
           >>> # non-square kernels and unequal stride and with padding
           >>> m = nn.Conv2d(16, 33, (3, 5), stride=(2, 1), padding=(4, 2))
           >>> # non-square kernels and unequal stride and with padding and dilation
           >>> m = nn.Conv2d(16, 33, (3, 5), stride=(2, 1), padding=(4, 2), dilation=(3, 1))
           >>> input = torch.randn(20, 16, 50, 100)
           >>> output = m(input)
       .. _cross-correlation:
           https://en.wikipedia.org/wiki/Cross-correlation
       .. _link:
           https://github.com/vdumoulin/conv_arithmetic/blob/master/README.md
       """

    """
    The very base class of all links
    """

    ITEM_TYPE = 'LINK'

    def __init__(self,
                 iden,
                 head=None,
                 width=2,
                 *args,
                 **kwargs):

        """

        """
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
        return 'Link(%s)'%(self._iden)

    @property
    def width(self):
        return self._attr['WIDTH']

    @width.setter
    def width(self, val):
        self._attr['WIDTH'] = val

    def set_width(self, val, head=True):
        if head and self.head:
            self.head.set_size_from_link(link_width=val)
            # w = self.width
            # scale = val/w
            # self.head.width *= scale
            # self.head.height *= scale

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
                print("[MOUSE EVENT] Selected!")
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
                ArrowClass = ArrowClassFactory.create(attr_head['TYPE'])
                head = ArrowClass.from_dict(attr_head)
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


class TwoNodeLink(BaseLink):

    ITEM_TYPE = 'TWO_NODE_LINK'

    def __init__(self, iden, source, target, *args, **kwargs):

        self._source = source
        self._target = target
        self.source.add_link(self)
        self.target.add_link(self)
        super().__init__(iden, *args, **kwargs)

    def __str__(self):
        str_link_type = self.ITEM_TYPE.replace('_', '').title()
        return "%s(%s, %s)"%(str_link_type, self.source.name, self.target.name)

    def __eq__(self, other):
        return id(other) == id(self)


    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, obj: BaseNode):
        if not obj.has_link(self):
            obj.add_link(self)
        self._source = obj

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, obj: BaseNode):
        if not obj.has_link(self):
            obj.add_link(self)
        self._target = obj

    # Read-only properties
    @property
    def pos_src(self):
        """
        The position of source relative to its parent link
        """
        return self._source.pos() - self.pos()

    @property
    def pos_tgt(self):
        """
        The position of target relative to its parent link
        """
        return self._target.pos() - self.pos()

    def is_node_selected(self):
        return self.source.isSelected() or self.target.isSelected()

    def are_nodes_close(self):
        """Decide whether the two nodes are overlapped
        to show the graphics of link appropriately.
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
