from qtpy.QtCore import Qt
from qtpy.QtCore import QObject
from qtpy.QtCore import Slot
from qtpy.QtWidgets import QGraphicsRectItem

from nezzle.graphics.screen import GraphicsScene
from nezzle.graphics.screen import GraphicsView
from nezzle.constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT


class SingleViewManager(QObject):

    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window

        self._tab_widget = self.mw.ui_mainTabWidget

        self.defaultScene = GraphicsScene()
        self.defaultScene.setSceneRect(0, 0, DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT)

        self.view = GraphicsView(main_window)
        self.view.setScene(self.defaultScene)

        self._is_empty = True
        self.tab_widget.addTab(self.view, "<Not selected>")
        self.tab_widget.setTabsClosable(False)

    @property
    def is_empty(self):
        return self._is_empty

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
        self._is_empty = True

    def set_current_view_scene(self, scene, text):
        if not scene:
            self.clear()
            return

        self.current_view.setScene(scene)
        self.set_current_view_text(text)
        self._is_empty = False

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


