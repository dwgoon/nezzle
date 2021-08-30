
from qtpy.QtCore import Qt
from qtpy.QtCore import QPointF
from qtpy.QtCore import QRectF

from qtpy.QtGui import QPen
from qtpy.QtGui import QFont
from qtpy.QtGui import QFontMetricsF
from qtpy.QtGui import QPainterPath
from qtpy.QtGui import QTextOption

from qtpy.QtGui import QColor
from qtpy.QtGui import QCursor

from qtpy.QtWidgets import QGraphicsItem
from qtpy.QtWidgets import QGraphicsSimpleTextItem
from qtpy.QtWidgets import QGraphicsTextItem
from qtpy.QtCore import QEvent

from nezzle.graphics.mixins import lockable
from nezzle.systemstate import get_system_state
from nezzle.graphics.baseitem import PainterOptionItem
from nezzle.graphics import BaseLink


@lockable
class TextLabel(PainterOptionItem):

    ITEM_TYPE = 'TEXT_LABEL'

    def __init__(self, parent, text, font=None, pos=None):
        self._text_item = QGraphicsTextItem()
        self._font = None

        super().__init__(parent=parent, iden=text)

        self._attr.set_trigger('TEXT',
                               self._trigger_set_text_str, when='set')
        self._attr.set_trigger('TEXT_COLOR',
                               self._trigger_set_text_color, when='set')
        self._attr.set_trigger('FONT',
                               self._trigger_set_font, when='set')
        self._attr.set_trigger('FONT_SIZE',
                               self._trigger_set_font_size, when='set')
        self._attr.set_trigger('FONT_FAMILY',
                               self._trigger_set_font_family, when='set')
        self._attr.set_trigger('FONT_BOLD',
                               self._trigger_set_font_bold, when='set')
        self._attr.set_trigger('FONT_ITALIC',
                               self._trigger_set_font_italic, when='set')

        if not font:
            font = QFont()
            font.setFamily('Arial')

        self.font = font

        if pos:
            self.setPos(pos)
            self._text_item.setPos(pos)

        self._text_item.setDefaultTextColor(Qt.black)

        self.setFlags(QGraphicsItem.ItemIsSelectable
                      | QGraphicsItem.ItemIsMovable
                      | QGraphicsItem.ItemIsFocusable
                      | QGraphicsItem.ItemSendsGeometryChanges)

        #self._text_item.setSelected(False)
        self._attr['TEXT'] = text

        self.update()

    # end of def __init__

    def __str__(self):
        return 'TextLabel(%s) belongs to %s'%(self.name, self.parentItem())

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, obj):
        self._attr['FONT'] = obj

    @property
    def text(self):
        return self._attr['TEXT']

    @text.setter
    def text(self, val):
        self._attr['TEXT'] = val

    @property
    def text(self):
        return self._attr['TEXT']

    @text.setter
    def text(self, val):
        self._attr['TEXT'] = val

    @property
    def text_item(self):
        return self._text_item

    def _trigger_set_x(self, key, value):
        self.setX(value)
        self._text_item.setX(value)
        self.update()
        return value

    def _trigger_set_y(self, key, value):
        self.setY(value)
        self._text_item.setY(value)
        self.update()
        return value

    def _trigger_set_font(self, key, value):

        if isinstance(value, QFont):
            self._font = QFont(value)
        elif isinstance(value, str):
            self._font = QFont()
            self._font.fromString(value)
        else:
            fstr = "%s is not allowed for setting font." % (type(value))
            raise ValueError(fstr)

        # Synchronize the properties related to the font.
        self._attr.set('FONT_SIZE', self._font.pixelSize(), trigger=False)
        self._attr.set('FONT_FAMILY', self._font.family(), trigger=False)
        self._attr.set('FONT_BOLD', self._font.bold(), trigger=False)
        self._attr.set('FONT_ITALIC', self._font.italic(), trigger=False)

        # update should be called to reflect the font
        # to that of self._text_item
        self.update()
        return self._font

    def _trigger_set_text_str(self, key, value):
        self._text_item.setPlainText(value)
        self.update()
        return value

    def _trigger_set_text_color(self, key, value):
        color = QColor(value)
        self._text_item.setDefaultTextColor(color)
        self.update()
        return color.name(QColor.HexArgb)

    def _trigger_set_font_size(self, key, value):
        self.font.setPixelSize(value)
        self.update()
        return value

    def _trigger_set_font_family(self, key, value):
        self.font.setFamily(value)
        self.update()
        return value

    def _trigger_set_font_bold(self, key, value):
        self.font.setBold(value)
        self.update()
        return value

    def _trigger_set_font_italic(self, key, value):
        self.font.setItalic(value)
        self.update()
        return value

    def setSelected(self, val):
        self._text_item.setSelected(val)
        super().setSelected(val)

    def boundingRect(self):
        return self._text_item.boundingRect()

    def shape(self):
        return self._text_item.shape()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)

        ## [DEBUG]
        # painter.setPen(Qt.red)
        # painter.setBrush(Qt.NoBrush)
        # painter.drawRect(self.boundingRect())
        ############################################

        self._text_item.paint(painter, option, widget)

    def is_movable(self):
        return True

    # def mousePressEvent(self, event):
    #     print("mousePressEvent of label")
    #     ss = get_system_state()
    #     if ss.is_locked(self.ITEM_TYPE):
    #         event.ignore()
    #         return
    #
    #     return super().mousePressEvent(event)
    #
    #     if event.button() == Qt.LeftButton:
    #         """
    #         The following check prevents this item being selected
    #         simply according to boundingRect.
    #         """
    #
    #         pos = event.pos() - self.pos()
    #         if self._path_paint.contains(pos):
    #             print("[MOUSE EVENT] Selected!")
    #             self.setSelected(True)
    #             event.accept()
    #     else:
    #         event.reject()


    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            parent = self.parentItem()
            if isinstance(parent, BaseLink):
                if parent.is_node_selected():
                    self._text_item.itemChange(change, self.pos())
                    return super().itemChange(change, self.pos())

        return super().itemChange(change, value)

    def update(self):
        if self._font:
            """ update() can be called although self._font is not initialized.
                For example, __init__ of a super class calls it
                to initialize the position.
            """
            self._text_item.setFont(self._font)
            self._text_item.update()
        self._invalidate()
        super().update()

    def copy(self, parent=None):
        if not parent:
            parent = self.parentItem()

        return self.from_dict(self.to_dict(), parent)

    def to_dict(self):
        attr = super().to_dict()
        attr['ID_PARENT'] = self.parentItem().iden
        attr['FONT'] = self._text_item.font().toString()
        return attr

    @classmethod
    def from_dict(cls, attr, parent):
        text = attr.pop('TEXT')

        strfont = attr.pop('FONT')
        font = QFont()
        font.fromString(strfont)

        obj = cls(parent, text, font)
        obj._attr.update(attr)
        return obj

    def align(self, mode="center"):
        rect = self._text_item.boundingRect()
        if mode == "center":
            #self.setPos(-rect.width() / 2, -rect.height() / 2)
            self._attr["POS_X"] = -rect.width() / 2
            self._attr["POS_Y"] = -rect.height() / 2

            self._attr["_OLD_POS"] = self.pos()



# @lockable
# class TextLabel(PainterOptionItem):
#
#     ITEM_TYPE = 'TEXT_LABEL'
#
#     def __init__(self, parent, text, font=None, pos=None):
#         #self._text_item = QGraphicsTextItem(parent=parent)
#         self._font = None
#
#         super().__init__(parent=parent, iden=text)
#
#         self._attr.set_trigger('TEXT',
#                                self._trigger_set_text_str, when='set')
#         self._attr.set_trigger('TEXT_COLOR',
#                                self._trigger_set_text_color, when='set')
#         self._attr.set_trigger('FONT',
#                                self._trigger_set_font, when='set')
#         self._attr.set_trigger('FONT_SIZE',
#                                self._trigger_set_font_size, when='set')
#         self._attr.set_trigger('FONT_FAMILY',
#                                self._trigger_set_font_family, when='set')
#         self._attr.set_trigger('FONT_BOLD',
#                                self._trigger_set_font_bold, when='set')
#         self._attr.set_trigger('FONT_ITALIC',
#                                self._trigger_set_font_italic, when='set')
#
#         if not font:
#             font = QFont()
#             font.setFamily('Arial')
#
#         self.font = font
#
#         if pos:
#             self.setPos(pos)
#             #self._text_item.setPos(pos)
#
#         #self._text_item.setDefaultTextColor(Qt.black)
#
#         self.setFlags(QGraphicsItem.ItemIsSelectable
#                       | QGraphicsItem.ItemIsMovable
#                       | QGraphicsItem.ItemIsFocusable
#                       | QGraphicsItem.ItemSendsGeometryChanges)
#
#         #self._text_item.setFlags(QGraphicsItem.ItemIsMovable
#         #                         | QGraphicsItem.ItemSendsGeometryChanges)
#
#         self._attr['TEXT'] = text
#
#
#         self._bounding_rect = QRectF()
#
#         self.update()
#     # end of def __init__
#
#     def __str__(self):
#         return 'TextLabel(%s) belongs to %s'%(self.name, self.parentItem())
#
#     @property
#     def font(self):
#         return self._font
#
#     @font.setter
#     def font(self, obj):
#         self._attr['FONT'] = obj
#
#     @property
#     def text(self):
#         return self._attr['TEXT']
#
#     @text.setter
#     def text(self, val):
#         self._attr['TEXT'] = val
#
#     def _trigger_set_x(self, key, value):
#         self.setX(value)
#         #self._text_item.setX(value)
#         self.update()
#         return value
#
#     def _trigger_set_y(self, key, value):
#         self.setY(value)
#         #self._text_item.setY(value)
#         self.update()
#         return value
#
#     def _trigger_set_font(self, key, value):
#
#         if isinstance(value, QFont):
#             self._font = QFont(value)
#         elif isinstance(value, str):
#             self._font = QFont()
#             self._font.fromString(value)
#         else:
#             fstr = "%s is not allowed for setting font." % (type(value))
#             raise ValueError(fstr)
#
#         # Synchronize the properties related to the font.
#         self._attr.set('FONT_SIZE', self._font.pointSizeF(), trigger=False)
#         self._attr.set('FONT_FAMILY', self._font.family(), trigger=False)
#         self._attr.set('FONT_BOLD', self._font.bold(), trigger=False)
#         self._attr.set('FONT_ITALIC', self._font.italic(), trigger=False)
#
#         # update should be called to reflect the font
#         # to that of self._text_item
#         self.update()
#         return self._font
#
#     def _trigger_set_text_str(self, key, value):
#         #self._text_item.setPlainText(value)
#         self.update()
#         return value
#
#     def _trigger_set_text_color(self, key, value):
#         color = QColor(value)
#         #self._text_item.setDefaultTextColor(color)
#         self.update()
#         return color.name(QColor.HexArgb)
#
#     def _trigger_set_font_size(self, key, value):
#         self.font.setPointSizeF(value)
#         self.update()
#         return value
#
#     def _trigger_set_font_family(self, key, value):
#         self.font.setFamily(value)
#         self.update()
#         return value
#
#     def _trigger_set_font_bold(self, key, value):
#         self.font.setBold(value)
#         self.update()
#         return value
#
#     def _trigger_set_font_italic(self, key, value):
#         self.font.setItalic(value)
#         self.update()
#         return value
#
#
#     def _update_bounding_rect(self):
#         # super()._update_bounding_rect()
#         #
#         # rect_cl_src = QRectF(self.pos_ctrl, self.pos_src)
#         # rect_cl_tgt = QRectF(self.pos_ctrl, self.pos_tgt)
#         #
#         # rect = self._bounding_rect
#         # rect = rect.united(rect_cl_src)
#         # rect = rect.united(rect_cl_tgt)
#         # self._bounding_rect = rect
#         fm = QFontMetricsF(self._font)
#         self._bounding_rect = fm.boundingRect(self._text)
#
#
#     def boundingRect(self):
#         #return self._text_item.boundingRect()
#         return self._bounding_rect
#
#     def shape(self):
#         #return self._text_item.shape()
#         return self._bounding_rect
#
#     def paint(self, painter, option, widget):
#         super().paint(painter, option, widget)
#         #self._text_item.paint(painter, option, widget)
#
#         painter.setFont(self._font)
#         painter.drawText()
#
#     def mousePressEvent(self, event):
#         ss = get_system_state()
#         if ss.is_locked(self.ITEM_TYPE):
#             event.ignore()
#         else:
#             return super().mousePressEvent(event)
#
#     def itemChange(self, change, value):
#         if change == QGraphicsItem.ItemPositionChange:
#             parent = self.parentItem()
#             if isinstance(parent, BaseLink):
#                 if parent.is_node_selected():
#                     #self._text_item.itemChange(change, self.pos())
#                     super().itemChange(change, self.pos())
#                     return
#
#             #self._text_item.setPos(value)
#             self.setPos(value)
#         # end of if
#
#         return super().itemChange(change, value)
#
#     def update(self):
#         if self._font:
#             """ update() can be called although self._font is not initialized.
#                 For example, __init__ of a super class calls it
#                 to initialize the position.
#             """
#             #self._text_item.setFont(self._font)
#             #self._text_item.update()
#
#         self._update_bounding_rect()
#         self._invalidate()
#         super().update()
#
#
#     def copy(self, parent=None):
#         if not parent:
#             parent = self.parentItem()
#
#         return self.from_dict(self.to_dict(), parent)
#
#     def to_dict(self):
#         attr = super().to_dict()
#         attr['ID_PARENT'] = self.parentItem().iden
#         # attr['FONT'] = self._text_item.font().toString()
#         attr['FONT'] = self._font.toString()
#         return attr
#
#     @classmethod
#     def from_dict(cls, attr, parent):
#         text = attr.pop('TEXT')
#
#         strfont = attr.pop('FONT')
#         font = QFont()
#         font.fromString(strfont)
#
#         obj = cls(parent, text, font)
#         obj._attr.update(attr)
#         return obj