
from qtpy.QtCore import QSizeF

from qtpy.QtGui import QFont
from qtpy.QtGui import QFontMetricsF


def update(nav, net):
    net_copy = net.copy()
    # myText->setItemFontSize(12);   // If I use font metrics I need to reset text size on every change, because resizing loses font info
    for iden, label in net_copy.labels.items():
        text = label._text_item
        str_text = text.toPlainText()
        textLength = len(str_text)
        fm = QFontMetricsF(text.font())
        fmRect = fm.tightBoundingRect(str_text.upper())
        fontHeight = fmRect.height()
        # without toUpper() the size is too small - even so it is a bit small
        # I read tightBoundingRect is slow - but boundingRect and height and ascent all give values that result in even smaller size
        # real absH = fm.ascent();
        absH = fmRect.height()
        absW = fmRect.width()
        rect = text.boundingRect()
        absHeightRatio = rect.height() / absH
        absWidthRatio = rect.width() / absW

        text.document().setPageSize(QSizeF(absWidthRatio * textLength, absHeightRatio * fontHeight));
        label.update()

    nav.append_item(net_copy)