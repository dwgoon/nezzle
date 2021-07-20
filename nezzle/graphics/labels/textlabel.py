# -*- coding:utf-8 -*-

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

from nezzle.graphics.mixins import Lockable
from nezzle.systemstate import get_system_state
from nezzle.graphics.mappableitem import PainterOptionItem
from nezzle.graphics import BaseLink

# @Lockable
# class TextLabel(QGraphicsSimpleTextItem):
#
#     #def __init__(self, parent, text, font=None, color=None, pos=None):
#     def __init__(self, parent, text, font=None, pos=None):
#         super().__init__(parent)
#
#         self.setText(text)
#
#         if pos:
#             self.setPos(pos)
#
#         if font:
#             self.setFont(font)
#
#         self.setFlags(QGraphicsItem.ItemIsSelectable
#                       | QGraphicsItem.ItemIsMovable
#                       | QGraphicsItem.ItemIsFocusable)
#
#         self._attr.set_trigger('TEXT',
#                                self._trigger_set_text_str, when='set')
#         self._attr.set_trigger('TEXT_COLOR',
#                                self._trigger_set_text_color, when='set')
#         self._attr.set_trigger('FONT_SIZE',
#                                self._trigger_set_font_size, when='set')
#         self._attr.set_trigger('FONT_FAMILY',
#                                self._trigger_set_font_family, when='set')
#         self._attr.set_trigger('FONT_BOLD',
#                                self._trigger_set_font_bold, when='set')
#         self._attr.set_trigger('FONT_ITALIC',
#                                self._trigger_set_font_italic, when='set')
#
#         self._attr['TEXT'] = text
#     # end of def __init__
#
#     @property
#     def parentIden(self):
#         return self.parent.iden
#
#     @property
#     def parent(self):
#         return super().parentItem()
#
#     # @property
#     # def color(self):
#     #     return self.brush().color()
#     #
#     # @color.setter
#     # def color(self, val):
#     #     self.setBrush(val)
#
#     @property
#     def font(self):
#         return super().font()
#
#     @font.setter
#     def font(self, val):
#         self.setFont(val)
#
#     @property
#     def text(self):
#         return super().text()
#
#     @text.setter
#     def text(self, val):
#         self.setText(val)
#
#     # def update(self, *args, **kwargs):
#     #     return super().update(*args, **kwargs)
#     #
#     # def mousePressEvent(self, event):
#     #     ss = get_system_state()
#     #     if ss.is_locked(self.lockType()):
#     #         event.ignore()
#     #     else:
#     #         return super().mousePressEvent(event)
#
#     def _trigger_set_text_str(self, key, value):
#         self._text = value
#         return value
#
#     def _trigger_set_text_color(self, key, value):
#         color = QColor(value)
#         self._pen_text.setColor(color)
#         return color.name(QColor.HexArgb)
#
#     def _trigger_set_font_size(self, key, value):
#         self._font.setPointSizeF(value)
#         return value
#
#     def _trigger_set_font_family(self, key, value):
#         self._font.setFamily(value)
#         return value
#
#     def _trigger_set_font_bold(self, key, value):
#         self._font.setBold(value)
#         return value
#
#     def _trigger_set_font_italic(self, key, value):
#         self._font.setItalic(value)
#         return value
#
#     def copy(self, parent=None):
#         if not parent:
#             parent = self.parentItem()
#
#         return __class__.from_dict(self._attr, parent)
#
#     def to_dict(self):
#         attr = super().to_dict()
#         attr['ID_PARENT'] = self.parentItem().iden
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

#
# @Lockable
# class TextLabel(PainterOptionItem):
#
#     ITEM_TYPE = 'TEXT_LABEL'
#
#     def __init__(self, parent, text, font=None, pos=None):
#         super().__init__(iden=text, parent=parent)
#         if font:
#             self._font = font
#         else:
#             self._font = QFont()
#             self._font.setFamily('Arial')
#
#         if pos:
#             self.setPos(pos)
#
#         self._pen_text = QPen()
#         self._pen_text.setBrush(Qt.black)
#
#         self.setFlags(QGraphicsItem.ItemIsSelectable
#                       | QGraphicsItem.ItemIsMovable
#                       | QGraphicsItem.ItemIsFocusable
#                       | QGraphicsItem.ItemSendsGeometryChanges)
#
#         self._attr.set_trigger('TEXT',
#                                self._trigger_set_text_str, when='set')
#         self._attr.set_trigger('TEXT_COLOR',
#                                self._trigger_set_text_color, when='set')
#         self._attr.set_trigger('FONT_SIZE',
#                                self._trigger_set_font_size, when='set')
#         self._attr.set_trigger('FONT_FAMILY',
#                                self._trigger_set_font_family, when='set')
#         self._attr.set_trigger('FONT_BOLD',
#                                self._trigger_set_font_bold, when='set')
#         self._attr.set_trigger('FONT_ITALIC',
#                                self._trigger_set_font_italic, when='set')
#
#         self._attr['TEXT'] = text
#     # end of def __init__
#
#
#     @property
#     def font(self):
#         return self._font
#
#     @font.setter
#     def font(self, obj):
#         self._font = obj
#
#     @property
#     def text(self):
#         return self._attr['TEXT']
#
#     @text.setter
#     def text(self, val):
#         self._attr['TEXT'] = val
#
#     def _trigger_set_text_str(self, key, value):
#         self._text = value
#         return value
#
#     def _trigger_set_text_color(self, key, value):
#         color = QColor(value)
#         self._pen_text.setColor(color)
#         return color.name(QColor.HexArgb)
#
#     def _trigger_set_font_size(self, key, value):
#         self._font.setPointSizeF(value)
#         return value
#
#     def _trigger_set_font_family(self, key, value):
#         self._font.setFamily(value)
#         return value
#
#     def _trigger_set_font_bold(self, key, value):
#         self._font.setBold(value)
#         return value
#
#     def _trigger_set_font_italic(self, key, value):
#         self._font.setItalic(value)
#         return value
#
#     def boundingRect(self):
#         fm = QFontMetricsF(self._font)
#         wp = self._pen.width()
#         width = fm.width(self._text) + 2*wp
#         height = fm.height() + 2*wp
#         rect = QRectF(-width/2, -height/2, width, height)
#         return rect
#
#     # def shape(self):
#     #     path = QPainterPath()
#     #     #path.addPath(self.path)
#     #
#     #     rect = self.boundingRect()
#     #     path.addRect(rect)
#     #     return path
#
#     def paint(self, painter, option, widget):
#         super().paint(painter, option, widget)
#
#         painter.setPen(self._pen_text)
#         painter.setFont(self._font)
#         fm = painter.fontMetrics()
#
#         # fm = QFontMetricsF(self._font)
#         rect_text = fm.boundingRect(self._text)
#         # width = fm.width(self._text)
#         # height = fm.height()
#         width = rect_text.width()
#         height = rect_text.height()
#         #rect_text = QRectF(-width/2, -height/2, width, height)
#         rect_text = QRectF(-width/2, -height/2, width, height)
#
#         #textOption = QTextOption()
#         #textOption.setUseDesignMetrics(True)
#         painter.drawText(rect_text, self._text)
#         #print("ID: ", id(self), "width: ", width, "height: ", height)
#         #painter.drawText(0, 0, width, height, Qt.AlignCenter, self._text)
#
#
#     # def itemChange(self, change, value):
#     #     if change == QGraphicsItem.ItemPositionChange:
#     #         self.scene().invalidate()
#     #     return super().itemChange(change, value)
#
#
#
#     def itemChange(self, change, value):
#
#         if change == QGraphicsItem.ItemPositionChange:
#             parent = self.parentItem()
#             if isinstance(parent, BaseLink):
#                 if parent.is_node_selected():
#                     return super().itemChange(change, self.pos())
#
#         return super().itemChange(change, value)
#
#     def copy(self, parent=None):
#         if not parent:
#             parent = self.parentItem()
#
#         return __class__.from_dict(self._attr, parent)
#
#     def to_dict(self):
#         attr = super().to_dict()
#         attr['ID_PARENT'] = self.parentItem().iden
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


@Lockable
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

        self._text_item.setFlags(QGraphicsItem.ItemIsMovable
                                 | QGraphicsItem.ItemSendsGeometryChanges)

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
        self._attr.set('FONT_SIZE', self._font.pointSizeF(), trigger=False)
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
        self.font.setPointSizeF(value)
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

    def boundingRect(self):
        return self._text_item.boundingRect()

    def shape(self):
        return self._text_item.shape()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        self._text_item.paint(painter, option, widget)

    def mousePressEvent(self, event):
        ss = get_system_state()
        if ss.is_locked(self.ITEM_TYPE):
            event.ignore()
        else:
            return super().mousePressEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            parent = self.parentItem()
            if isinstance(parent, BaseLink):
                if parent.is_node_selected():
                    self._text_item.itemChange(change, self.pos())
                    super().itemChange(change, self.pos())
                    return

            self._text_item.setPos(value)
        # end of if

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
