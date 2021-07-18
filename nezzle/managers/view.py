
from qtpy.QtCore import Qt
from qtpy.QtCore import QObject
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QGraphicsRectItem


from nezzle.graphics.screen import GraphicsScene
from nezzle.graphics.screen import GraphicsView
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT


# class GraphicsViewManager(QObject):
#
#     def __init__(self, mainWindow, tab_widget):
#         super().__init__(parent=mainWindow)
#         self.mw = mainWindow
#         self._tab_widget = tab_widget
#         self.tab_widget.tabCloseRequested.connect(self.closeTab)
#         self.defaultScene = GraphicsScene()
#         self.defaultScene.setSceneRect(0, 0,
#                                        DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT)
#         self.defaultView = GraphicsView()
#         self.defaultView.set_current_view_scene(self.defaultScene)
#         self.tab_widget.addTab(self.defaultView, "")
#         self.isEmpty = True
#
#     @property
#     def tab_widget(self):
#         return self._tab_widget
#
#     @property
#     def isEmpty(self):
#         return self._isEmpty
#
#     @isEmpty.setter
#     def isEmpty(self, b):
#         self._isEmpty = b
#         if b:
#             self.tab_widget.setTabsClosable(False)
#         else:
#             self.tab_widget.setTabsClosable(True)
#
#     @property
#     def current_view(self):
#         if self.isEmpty:
#             return None
#
#         return self.tab_widget.currentWidget()
#
#     @Slot(int)
#     def closeTab(self, currentIndex):
#         print("closeTab: ", currentIndex)
#         current_view = self.tab_widget.widget(currentIndex)
#         #if current_view == self.defaultView:
#          #   return
#
#         if current_view:
#             self.tab_widget.removeTab(currentIndex)
#             current_view.close()
#             current_view.deleteLater()
#             self.mw.nt_manager.clear_selection()
#
#             if self.tab_widget.count() == 0:
#                 self.isEmpty = True
#                 self.tab_widget.addTab(self.defaultView, "")
#
#
#
#         # [REF] http://stackoverflow.com/questions/25635485/pyqt-close-unselected-tab
#
#
#     def appendView(self, view, label):
#         if self.isEmpty:
#             self.tab_widget.removeTab(0)
#             self.isEmpty = False
#
#         self.tab_widget.addTab(view, label)
#         self.tab_widget.setCurrentWidget(view)
#
#     def set_current_view_scene(self, scene, text):
#         if not self.isEmpty:
#             self.current_view.set_current_view_scene(scene)
#             index = self.tab_widget.currentIndex()
#             self.tab_widget.setTabText(index, text)


class SingleViewManager(QObject):

    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window

        self._tab_widget = self.mw.ui_mainTabWidget
        self.defaultScene = GraphicsScene()
        self.defaultScene.setSceneRect(0, 0,
                                       DEFAULT_SCENE_WIDTH,
                                       DEFAULT_SCENE_HEIGHT)
        self.view = GraphicsView(main_window)
        self.view.setScene(self.defaultScene)
        self._isEmpty = True
        self.tab_widget.addTab(self.view, "<Not selected>")
        self.tab_widget.setTabsClosable(False)

    @property
    def isEmpty(self):
        return self._isEmpty

    @property
    def tab_widget(self):
        return self._tab_widget

    @property
    def current_view(self):
        return self.tab_widget.currentWidget()

    def clear(self):
        self.defaultScene.clear()
        self.current_view.setScene(self.defaultScene)
        self.set_current_view_text("<Not selected>")
        self._isEmpty = True

    def set_current_view_scene(self, scene, text):
        if not scene:
            self.clear()
            return

        self.current_view.setScene(scene)
        self.set_current_view_text(text)
        self._isEmpty = False

        """
        To see the area of scene
        
        rect_item = QGraphicsRectItem(-scene.width()/2, -scene.height()/2,
                                       scene.width(), scene.height())
        rect_item.setPen(Qt.red)
        rect_item.setPos(scene.width()/2, scene.height()/2)
        scene.addItem(rect_item)
        """

    def set_current_view_text(self, text):
        index = self.tab_widget.currentIndex()
        self.tab_widget.setTabText(index, text)


