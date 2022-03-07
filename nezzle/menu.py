import os
import sys
from traceback import format_exc

from qtpy.QtCore import Qt
from qtpy.QtCore import QMimeData
from qtpy.QtCore import QBuffer
from qtpy.QtCore import QByteArray
from qtpy.QtCore import QIODevice
from qtpy.QtCore import Slot

from qtpy.QtWidgets import QWidget
from qtpy.QtWidgets import QMessageBox
from qtpy.QtWidgets import QDialog, QFileDialog
from qtpy.QtWidgets import QApplication

from qtpy.QtGui import QKeySequence
from qtpy.QtGui import QImage
from qtpy.QtGui import QPainter
from qtpy.QtGui import QClipboard

from nezzle.dialogs.opennetworkdialog import OpenNetworkDialog
from nezzle.dialogs.exportimagedialog import ExportImageDialog

from nezzle.io import io
from nezzle.systemstate import get_system_state
from nezzle.constants import Lock

from nezzle.graphics.nodes.nodeconverter import NodeConverter
from nezzle.graphics.nodes.basenode import BaseNode
from nezzle.graphics.nodes.ellipsenode import EllipseNode
from nezzle.graphics.nodes.rectanglenode import RectangleNode

from nezzle.graphics.links.linkconverter import LinkConverter
from nezzle.graphics.links.baselink import BaseLink
from nezzle.graphics.links.straightlink import StraightLink
from nezzle.graphics.links.curvedlink import CurvedLink
from nezzle.graphics.links.elbowlink import VerticalElbowLink, HorizontalElbowLink


class MenuActionHandler(QWidget):
    """
    MenuActionHandler should be a subclass of QWidget,
    otherwise @Slot decorator does not work for the instance methods.
    """

    def __init__(self, mw):
        super().__init__()
        self.mw = mw
        self.initialize_actions()
        self.openNetworkDialog = OpenNetworkDialog(parent=self.mw)
        self.exportImageDialog = ExportImageDialog(parent=self.mw)

    def initialize_actions(self):
        # File
        self.mw.ui_actionOpenNetwork.triggered.connect(
            self.process_open_network)
        self.mw.ui_actionSaveNetwork.triggered.connect(
            self.process_save_network)
        self.mw.ui_actionExportImage.triggered.connect(
            self.process_export_image)

        # Edit
        # self.mw.history_manager.actionUndo.triggered.connect(self.procees_undo)
        # self.mw.history_manager.actionRedo.triggered.connect(self.process_redo)

        self.mw.ui_actionUndo.triggered.connect(self.process_undo)
        self.mw.ui_actionRedo.triggered.connect(self.process_redo)

        self.mw.ui_actionUndo.setShortcuts(QKeySequence.Undo)
        self.mw.ui_actionRedo.setShortcuts(QKeySequence.Redo)

        self.mw.ui_actionCopy.triggered.connect(self.process_copy)
        self.mw.ui_actionCopy.setShortcut(QKeySequence('Ctrl+C'))

        self.mw.ui_actionPaste.triggered.connect(self.process_paste)
        self.mw.ui_actionPaste.setShortcut(QKeySequence('Ctrl+V'))

        # View
        self.mw.ui_actionViewNavigationDock.triggered.connect(
            self.process_view_navigation_dock
        )
        self.mw.ui_navigationDock.closeEventOccured.connect(
             self.process_view_navigation_dock
        )

        self.mw.ui_actionViewConsoleDock.triggered.connect(
            self.process_view_console_dock
        )
        self.mw.ui_consoleDock.closeEventOccured.connect(
             self.process_view_console_dock
        )

        self.mw.ui_actionViewHistoryDock.triggered.connect(
            self.process_view_history_dock
        )
        self.mw.ui_historyDock.closeEventOccured.connect(
             self.process_view_history_dock
        )

        # Select -> Lock -> Lock Nodes, Lock Links, Lock Labels
        self.mw.ui_actionLockNodes.triggered.connect(
            self.process_lock_nodes
        )
        self.mw.ui_actionLockLinks.triggered.connect(
            self.process_lock_links
        )
        self.mw.ui_actionLockLabels.triggered.connect(
            self.process_lock_labels
        )

        # Select -> Convert -> To
        self.mw.ui_actionToEllipseNode.triggered.connect(
            self.process_convert_to_ellipse_node
        )
        self.mw.ui_actionToRectangleNode.triggered.connect(
            self.process_convert_to_rectangle_node
        )
        self.mw.ui_actionToStraightLink.triggered.connect(
            self.process_convert_to_straight_link
        )
        self.mw.ui_actionToCurvedLink.triggered.connect(
            self.process_convert_to_curved_link
        )
        self.mw.ui_actionToVerticalElbowLink.triggered.connect(
            self.process_convert_to_vertical_elbow_link
        )
        self.mw.ui_actionToHorizontalElbowLink.triggered.connect(
            self.process_convert_to_horizontal_elbow_link
        )


        # Select -> Select All
        self.mw.ui_actionSelectAll.triggered.connect(
            self.process_select_all
        )
        self.mw.ui_actionSelectAll.setShortcut(QKeySequence('Ctrl+A'))


        # The following objects are locked at first.
        self.mw.ui_actionLockLinks.setChecked(True)
        self.process_lock_links(True)

        self.mw.ui_actionLockLabels.setChecked(True)
        self.process_lock_labels(True)

        # Layout -> Align
        self.mw.ui_actionAlignLeft.triggered.connect(
            self.process_align_left)
        self.mw.ui_actionAlignCenter.triggered.connect(
            self.process_align_center)
        self.mw.ui_actionAlignRight.triggered.connect(
            self.process_align_right)

        self.mw.ui_actionAlignTop.triggered.connect(
            self.process_align_top)
        self.mw.ui_actionAlignMiddle.triggered.connect(
            self.process_align_middle)
        self.mw.ui_actionAlignBottom.triggered.connect(
            self.process_align_bottom)

        self.mw.ui_actionDistributeHorizontally.triggered.connect(
            self.process_distribute_horizontally)
        self.mw.ui_actionDistributeVertically.triggered.connect(
            self.process_distribute_vertically)

        self.mw.ui_menuAlign.setEnabled(False)

    @Slot()
    def process_undo(self):
        #self.mw.history_manager.undo()
        self.mw.sv_manager.view.undo_current_scene()

    @Slot()
    def process_redo(self):
        #self.mw.history_manager.redo()
        self.mw.sv_manager.view.redo_current_scene()

    # TODO: Implement Copy & Paste QGraphicsItem to the clipboard
    @Slot()
    def process_copy(self):
        # TODO: Implement copy function for copying inside the scene.
        item = self.mw.nt_manager.current_item
        if not item:
            return

        net = item.data()
        scene = net.scene
        scene.clearSelection()
        scene.clearFocus()
        brect = scene.itemsBoundingRect()
        brect.adjust(-5, -5, +10, +10)

        # Create a buffer
        data = QByteArray()
        buffer = QBuffer(data)
        buffer.open(QIODevice.WriteOnly)

        scale_width = 200
        scale_height = 200
        dpi_width = 300
        dpi_height = 300
        image = QImage((scale_width / 100.0) * brect.width(),
                       (scale_height / 100.0) * brect.height(),
                       QImage.Format_ARGB32_Premultiplied)

        # dpm = 300 / 0.0254 # ~300 DPI
        dpm_width = dpi_width / 0.0254
        dpm_height = dpi_height / 0.0254
        image.setDotsPerMeterX(dpm_width)
        image.setDotsPerMeterY(dpm_height)
        # bbrush = scene.backgroundBrush()
        # image.fill(bbrush.color())
        image.fill(Qt.transparent)

        painter = QPainter()
        painter.begin(image)
        painter.setOpacity(0.0)
        painter.setRenderHints(QPainter.TextAntialiasing
                               | QPainter.Antialiasing
                               | QPainter.SmoothPixmapTransform
                               | QPainter.HighQualityAntialiasing)

        scene.render(painter, source=brect)
        painter.end()
        image.save(buffer, "PNG")

        cb = QApplication.clipboard()
        mime_data = QMimeData()
        if sys.platform == "win32":
            mime_data.setData("PNG", buffer.buffer())
            cb.setMimeData(mime_data, QClipboard.Clipboard)
        else:
            mime_data.setImageData(image)
            cb.setImage(image, QClipboard.Clipboard)



    @Slot()
    def process_paste(self):
        #TODO: Implement paste function
        pass

    @Slot(bool)
    def process_open_network(self):

        while True:
            self.openNetworkDialog.exec()
            choice = self.openNetworkDialog.result()
            if choice == QDialog.Rejected:
                 return

            fpath = self.openNetworkDialog.fpath

            if choice == QDialog.Rejected:
                break
            elif choice == QDialog.Accepted:
                fpath = fpath.strip()
                try:
                    net = io.read_network(fpath, self.openNetworkDialog.link_map)
                except Exception as err:
                    err_msg = "An error has occurred during opening the file.\n%s"
                    self.show_error("Open a network file", err_msg % format_exc())
                    continue

                network_name = self.openNetworkDialog.network_name
                if network_name:
                    net.name = network_name
                else:
                    net.name = os.path.basename(fpath)

                self.mw.sv_manager.set_current_view_scene(net.scene, net.name)
                self.mw.nt_manager.append_item(net)
                # self.mw.ct_manager.update_console_variables()

            # end of if
            break
        # end of while


    @Slot(bool)
    def process_save_network(self):
        try:
            fpath = QFileDialog.getSaveFileName(self.mw,
                                                self.tr("Save a network file"),
                                                "",
                                                self.tr("Network files (*.sif *.json)"))
            fpath = fpath[0]
            if fpath:
                net = self.mw.nt_manager.current_item.data()
                if net:
                    io.write_network(net, fpath)
                else:
                    err_msg = "There is no selected network."
                    self.show_error("Save a network", err_msg)
            # end of if
        except Exception as err:
            err_msg = "An error has occurred during saving the file:\n%s"
            self.show_error("Save a network file", err_msg % format_exc())

    @Slot(bool)
    def process_export_image(self):
        try:
            self.exportImageDialog.exec()

            if self.exportImageDialog.result() == QDialog.Rejected:
                return

            net = self.mw.nt_manager.current_item.data()
            if net:
                fpath = self.exportImageDialog.fpath
                is_transparent = self.exportImageDialog.isTransparent
                quality = self.exportImageDialog.quality
                scale_width = self.exportImageDialog.scaleWidth
                scale_height = self.exportImageDialog.scaleHeight
                dpi_width = self.exportImageDialog.dpiWidth
                dpi_height = self.exportImageDialog.dpiHeight
                if not fpath:
                    err_msg = "File name is not designated."
                    self.show_error("Export a network image", err_msg)

                io.write_image(net,
                                   fpath,
                                   is_transparent,
                                   quality,
                                   scale_width, scale_height,
                                   dpi_width, dpi_height)
        except Exception as err:
            err_msg = "An error has occurred during saving the file:\n%s"
            self.show_error("Export a network image", err_msg % format_exc())

        # end of except

    def show_error(self, title, err_msg):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(err_msg)
        msg.exec()

    @Slot(bool)
    def process_view_navigation_dock(self, checked):
        if checked:
            self.mw.ui_navigationDock.show()
        else:
            self.mw.ui_navigationDock.hide()
        self.mw.ui_actionViewNavigationDock.setChecked(checked)

    @Slot(bool)
    def process_view_console_dock(self, checked):
        if checked:
            self.mw.ui_consoleDock.show()
        else:
            self.mw.ui_consoleDock.hide()
        self.mw.ui_actionViewConsoleDock.setChecked(checked)

    @Slot(bool)
    def process_view_history_dock(self, checked):
        if checked:
            self.mw.ui_historyDock.show()
        else:
            self.mw.ui_historyDock.hide()

        self.mw.ui_actionViewHistoryDock.setChecked(checked)

    @Slot(bool)
    def process_lock_nodes(self, checked):
        ss = get_system_state()
        ss.set_locked(Lock.NODES, checked)

    @Slot(bool)
    def process_lock_labels(self, checked):
        ss = get_system_state()
        ss.set_locked(Lock.LABELS, checked)

    @Slot(bool)
    def process_lock_links(self, checked):
        ss = get_system_state()
        ss.set_locked(Lock.LINKS, checked)

    def _process_convert_to_node(self, nodeclass):
        net = self.mw.nt_manager.current_net
        if not net:
            return

        # scene = net.scene
        # for obj in scene.selectedItems():
        #     if not isinstance(obj, BaseNode):
        #         continue
        #
        #     if type(obj) == nodeclass:
        #         continue
        #
        #     new_node = NodeConverter.convert(obj, nodeclass)
        #     net.replace_node(obj, new_node)
        # # end of for
        scene = net.scene

        old_items = []
        new_items = []
        for old_item in scene.selectedItems():
            if not isinstance(old_item, BaseNode):
                continue

            if type(old_item) == nodeclass:
                continue

            new_item = NodeConverter.convert(old_item, nodeclass)
            old_items.append(old_item)
            new_items.append(new_item)
        # end of for
        if len(old_items) > 0:
            self.mw.hv_manager.history.on_convert_nodes(net, old_items, new_items)

    @Slot()
    def process_convert_to_ellipse_node(self):
        self._process_convert_to_node(EllipseNode)

    @Slot()
    def process_convert_to_rectangle_node(self):
        self._process_convert_to_node(RectangleNode)

    def _process_convert_to_link(self, linkclass):
        net = self.mw.nt_manager.current_net
        if not net:
            return

        scene = net.scene

        old_items = []
        new_items = []
        for old_item in scene.selectedItems():
            if not isinstance(old_item, BaseLink):
                continue

            if type(old_item) == linkclass:
                continue

            new_item = LinkConverter.convert(old_item, linkclass)
            old_items.append(old_item)
            new_items.append(new_item)
        # end of for
        if len(old_items) > 0:
            self.mw.hv_manager.history.on_convert_links(net, old_items, new_items)

    @Slot()
    def process_convert_to_straight_link(self):
        self._process_convert_to_link(StraightLink)

    @Slot()
    def process_convert_to_curved_link(self):
        self._process_convert_to_link(CurvedLink)

    @Slot()
    def process_convert_to_vertical_elbow_link(self):
        self._process_convert_to_link(VerticalElbowLink)

    @Slot()
    def process_convert_to_horizontal_elbow_link(self):
        self._process_convert_to_link(HorizontalElbowLink)

    @Slot(bool)
    def process_select_all(self):
        item = self.mw.nt_manager.current_item
        if not item:
            return

        net = item.data()
        scene = net.scene
        for graphics_item in scene.items():
            graphics_item.setSelected(True)

    @Slot()
    def process_align_left(self):
        self.mw.sv_manager.view.align_objects('left')

    @Slot()
    def process_align_center(self):
        self.mw.sv_manager.view.align_objects('center')

    @Slot()
    def process_align_right(self):
        self.mw.sv_manager.view.align_objects('right')

    @Slot()
    def process_align_top(self):
        self.mw.sv_manager.view.align_objects('top')

    @Slot()
    def process_align_middle(self):
        self.mw.sv_manager.view.align_objects('middle')

    @Slot()
    def process_align_bottom(self):
        self.mw.sv_manager.view.align_objects('bottom')

    @Slot()
    def process_distribute_horizontally(self):
        self.mw.sv_manager.view.distribute_objects('horizontal')

    @Slot()
    def process_distribute_vertically(self):
        self.mw.sv_manager.view.distribute_objects('vertical')


