# -*- coding: utf-8 -*-

from qtpy.QtCore import Qt
from qtpy.QtGui import QColor

from nezzle.utils import Singleton

@Singleton
class AttributeMapper(object):
    def __init__(self):
        self._map_to_qt = {}

        # BORDER_JOIN
        self._map_to_qt['BORDER_JOIN'] = {}
        self._map_to_qt['BORDER_JOIN']['BEVEL'] = Qt.BevelJoin
        self._map_to_qt['BORDER_JOIN']['MITER'] = Qt.MiterJoin
        self._map_to_qt['BORDER_JOIN']['ROUND'] = Qt.RoundJoin

        # self._map_to_str['BORDER_JOIN'] = {}
        # self._map_to_str['BORDER_JOIN'][Qt.BevelJoin] = 'BEVEL'
        # self._map_to_str['BORDER_JOIN'][Qt.MiterJoin] = 'MITER'
        # self._map_to_str['BORDER_JOIN'][Qt.RoundJoin] = 'ROUND'

        # LINE_TYPE
        self._map_to_qt['BORDER_LINE'] = {}
        self._map_to_qt['BORDER_LINE']['SOLID'] = Qt.SolidLine
        self._map_to_qt['BORDER_LINE']['DASH'] = Qt.DashLine
        self._map_to_qt['BORDER_LINE']['DOT'] = Qt.DotLine
        self._map_to_qt['BORDER_LINE']['DASHDOT'] = Qt.DashDotLine
        self._map_to_qt['BORDER_LINE']['DASHDOTDOT'] = Qt.DashDotDotLine

        # Create a mapper vice versa.
        self._map_to_str = {}
        for attr, options in self._map_to_qt.items():
            self._map_to_str[attr] = {}
            d = {qtobj:strval for strval, qtobj in options.items()}
            self._map_to_str[attr] = d

        
    def to_qt(self, attr, val):
        """
        e.g.) to_qt('BORDER_JOIN', 'BEVEL') => Qt.BevelJoin
        e.g.) to_qt('BORDER_COLOR', '#000000') => QColor('#000000')

        """
        if not isinstance(val, str):
            raise ValueError("Converting to an Qt Object "
                             "requires Python string, not %s"%(val))

        attr = attr.upper()
        val = val.upper()
        if attr.endswith('_COLOR'):
            return self._to_qcolor(attr, val)

        if attr in self._map_to_qt:
            return self._map_to_qt[attr][val]
        else:
            raise AttributeError("It is not a valid attribute.")


    def to_str(self, attr, obj):

        attr = attr.upper()
        if attr.endswith('_COLOR'):
            return self._to_color_str(attr, obj)

        if attr in self._map_to_str:
            return self._map_to_str[attr][obj]
        else:
            raise AttributeError("It is not a valid attribute.")

    def _to_qcolor(self, attr, val):
        if not QColor.isValidColor(val):
            raise AttributeError("It is not a valid color string: %s"%(val))

        color = QColor(val)
        return color

    def _to_color_str(self, obj):
        if isinstance(obj, QColor):
            return obj.name(QColor.HexArgb)
        elif isinstance(obj, Qt.GlobalColor):
            color = QColor(obj)
            return color.name(QColor.HexArgb)
        else:
            raise AttributeError("It is not a valid Qt color object: %s"%(obj))

