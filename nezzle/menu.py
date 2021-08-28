import os
from traceback import format_exc

from qtpy.QtWidgets import QWidget
from qtpy.QtWidgets import QMessageBox
from qtpy.QtWidgets import QDialog, QFileDialog
from qtpy.QtWidgets import QApplication

from qtpy.QtGui import QKeySequence
from qtpy.QtGui import QImage
from qtpy.QtGui import QPainter
from qtpy.QtGui import QClipboard

from qtpy.QtCore import Qt
from qtpy.QtCore import QSize
from qtpy.QtCore import QRectF
from qtpy.QtCore import QMimeData
from qtpy.QtCore import QBuffer
from qtpy.QtCore import QDataStream
from qtpy.QtCore import QByteArray
from qtpy.QtCore import QIODevice
from qtpy.QtCore import Signal, Slot
from qtpy.QtCore import QRectF

from qtpy.QtSvg import QSvgGenerator

from nezzle.dialogs.opennetworkdialog import OpenNetworkDialog
from nezzle.dialogs.exportimagedialog import ExportImageDialog

from nezzle.graphics.screen import GraphicsScene
from nezzle.graphics.screen import GraphicsView
from nezzle import fileio
from nezzle.systemstate import get_system_state
from nezzle.constants import Lock

from nezzle.graphics.nodes.nodeconverter import NodeConverter
from nezzle.graphics.nodes.basenode import BaseNode
from nezzle.graphics.nodes.ellipsenode import EllipseNode
from nezzle.graphics.nodes.rectangleenode import RectangleNode

from nezzle.graphics.links.linkconverter import LinkConverter
from nezzle.graphics.links.baselink import BaseLink
from nezzle.graphics.links.selflooplink import SelfloopLink
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

        # self.mw.ui_actionUndo.triggered.connect(self.process_undo)
        # self.mw.ui_actionRedo.triggered.connect(self.process_redo)

        self.mw.sv_manager.view.items_moved_by_mouse.connect(
            self.mw.history_manager.on_items_moved_by_mouse
        )
        self.mw.sv_manager.view.items_moved_by_key.connect(
            self.mw.history_manager.on_items_moved_by_key
        )

        #self.mw.view.item_removed.connect(self.mw.history_manager.on_item_removed)

        self.mw.ui_actionCopy.triggered.connect(self.process_copy)
        self.mw.ui_actionCopy.setShortcut(QKeySequence('Ctrl+C'))

        self.mw.ui_actionPaste.triggered.connect(self.process_paste)
        self.mw.ui_actionPaste.setShortcut(QKeySequence('Ctrl+V'))

        # View
        self.mw.ui_actionViewNetworksDock.triggered.connect(
            self.process_view_networks_dock
        )
        self.mw.ui_actionViewConsoleDock.triggered.connect(
            self.process_view_console_dock
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

    # @Slot()
    # def process_undo(self):
    #     self.mw.history_manager.undo()
    #
    # @Slot()
    # def process_redo(self):
    #     self.mw.history_manager.redo()

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
        brect = scene.itemsBoundingRect()
        brect.adjust(-5, -5, +10, +10)

        width = brect.width()
        height = brect.height()

        # Create a buffer
        data = QByteArray()
        b = QBuffer(data)
        b.open(QIODevice.WriteOnly)

        # Create SVG
        svgGen = QSvgGenerator()
        svgGen.setOutputDevice(b)
        svgGen.setSize(QSize(width, height))
        svgGen.setViewBox(QRectF(0.0, 0.0, width, height))

        painter = QPainter()
        painter.begin(svgGen)
        painter.setBackgroundMode(Qt.TransparentMode)  # Added
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        scene.render(painter)
        painter.end()

        mimeData = QMimeData()
        mimeData.setData("image/svg+xml", b.buffer())
        QApplication.clipboard().setMimeData(mimeData, QClipboard.Clipboard)

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
                    net = fileio.read_network(fpath, self.openNetworkDialog.link_map)
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
                    fileio.write_network(net, fpath)
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

                fileio.write_image(net,
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
    def process_view_networks_dock(self, checked):
        self.mw.ui_netDock.setVisible(checked)

    @Slot(bool)
    def process_view_console_dock(self, checked):
        self.mw.ui_consoleDock.setVisible(checked)

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
        item = self.mw.nt_manager.current_item
        if not item:
            return

        net = item.data()
        scene = net.scene
        for obj in scene.selectedItems():
            if not isinstance(obj, BaseNode):
                continue

            if type(obj) == nodeclass:
                continue

            new_node = NodeConverter.to_node(obj, nodeclass)
            net.replace_node(obj, new_node)
        # end of for

    @Slot()
    def process_convert_to_ellipse_node(self):
        self._process_convert_to_node(EllipseNode)

    @Slot()
    def process_convert_to_rectangle_node(self):
        self._process_convert_to_node(RectangleNode)

    def _process_convert_to_link(self, linkclass):
        item = self.mw.nt_manager.current_item
        if not item:
            return

        net = item.data()
        scene = net.scene
        for obj in scene.selectedItems():
            if not isinstance(obj, BaseLink):
                continue

            if type(obj) == linkclass:
                continue

            new_link = LinkConverter.to_link(obj, linkclass)
            net.remove_link(obj)
            net.add_link(new_link)
        # end of for

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


