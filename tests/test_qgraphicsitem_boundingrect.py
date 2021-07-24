import sys
from PyQt5 import QtGui, QtCore, QtWidgets

class GraphicsItem(QtWidgets.QGraphicsItem):
    """
     From the QT docs:
     To write your own graphics item, you first create a subclass
     of QGraphicsItem, and then start by implementing its two pure
     virtual public functions: boundingRect(), which returns an estimate
     of the area painted by the item, and paint(),
     which implements the actual painting.
    """
    # call constructor of GraphicsItem
    def __init__(self, rect, pen, brush, tooltip='No tip here', parent=None):
        # call constructor of QGraphicsItem
        super(GraphicsItem, self).__init__()

        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsFocusable, True)

        self.setAcceptHoverEvents(True)

        self.pen = pen
        pw = self.pen.widthF()
        self.brush = QtGui.QBrush(QtCore.Qt.blue)
        self.brush = brush
        self.setToolTip(tooltip)
        self.parent = parent

        self.rect = QtCore.QRectF(rect[0], rect[1], rect[2], rect[3])
        self.focusrect = QtCore.QRectF(rect[0]-pw/2, rect[1]-pw/2,
                rect[2]+pw, rect[3]+pw)

    def mouseMoveEvent(self, event):
        # move object
        QtWidgets.QGraphicsItem.mouseMoveEvent(self, event)

    def mousePressEvent(self, event):
        # select object
        # set item as topmost in stack
        self.setZValue(self.parent.scene.items()[0].zValue() + 1)
        self.setSelected(True)
        QtWidgets.QGraphicsItem.mousePressEvent(self, event)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)
        if self.isSelected():
            self.drawFocusRect(painter)

    def drawFocusRect(self, painter):
        self.focusbrush = QtGui.QBrush()
        self.focuspen = QtGui.QPen(QtCore.Qt.DotLine)
        self.focuspen.setColor(QtCore.Qt.black)
        self.focuspen.setWidthF(1.5)
        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)
        painter.drawRect(self.focusrect)

    def hoverEnterEvent(self, event):
        self.pen.setStyle(QtCore.Qt.DotLine)
        QtWidgets.QGraphicsItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        self.pen.setStyle(QtCore.Qt.SolidLine)
        QtWidgets.QGraphicsItem.hoverLeaveEvent(self, event)


class MyMainWindow(QtWidgets.QMainWindow):
    # call constructor of MyMainWindow
    def __init__(self, parent=None):
        # call constructor of QMainWindow
        super(MyMainWindow, self).__init__(parent)

        w = 1000
        h = 800
        self.scene = QtWidgets.QGraphicsScene(-w/2, -h/2, w, h)

        self.view = QtWidgets.QGraphicsView()
        # set QGraphicsView attributes
        self.view.setRenderHints(QtGui.QPainter.Antialiasing |
            QtGui.QPainter.HighQualityAntialiasing)
        self.view.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.view.setScene(self.scene)

        # set central widget for the application
        self.setCentralWidget(self.view)

        # add items to the scene
        self.addGraphicsItem((0, 0, 250, 250), 8.0, (255, 0, 0), (0, 0, 255), 'My first item')
        self.addGraphicsItem((-250, -250, 300, 200), 4.0, (0, 0, 0), (255, 0, 100), 'My 2nd item')
        self.addGraphicsItem((200, -200, 200, 200), 10.0, (0, 0, 255), (0, 255, 100), 'My 3rd item')

    def addGraphicsItem(self, rect, pw, pc, bc, tooltip):
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setColor(QtGui.QColor(pc[0], pc[1], pc[2], 255))
        pen.setWidth(pw)
        brush = QtGui.QBrush(QtGui.QColor(bc[0], bc[1], bc[2], 255))
        item = GraphicsItem(rect, pen, brush, tooltip, self)
        self.scene.addItem(item)

    def mousePressEvent(self, event):
        #print 'from MainWindow'
        pass


def main():
    app = QtWidgets.QApplication(sys.argv)
    form = MyMainWindow()
    form.setGeometry(700, 100, 1050, 850)
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()