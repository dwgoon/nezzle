# -*- coding: utf-8 -*-
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
from qtpy.QtCore import QRectF
from qtpy.QtCore import QMimeData
from qtpy.QtCore import QBuffer
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


class MenuActionHandler(QWidget):
    """
    MenuActionHandler should be a subclass of QWidget,
    otherwise @Slot decorator does not work for the instance methods.
    """

    def __init__(self, mainWindow):
        super().__init__()
        self.mw = mainWindow
        self.initialize_actions()
        self.openNetworkDialog = OpenNetworkDialog(parent=self.mw)
        self.exportImageDialog = ExportImageDialog(parent=self.mw)
        
        
    def initialize_actions(self):
        #self.mw.ui_actionNewView.triggered.connect(self.processNewView)


        # File
        self.mw.ui_actionOpenNetwork.triggered.connect(
            self.process_open_network)
        self.mw.ui_actionSaveNetwork.triggered.connect(
            self.process_save_network)
        self.mw.ui_actionExportImage.triggered.connect(
            self.process_export_image)


        # Edit
        self.mw.ui_actionCopy.triggered.connect(self.process_copy)
        self.mw.ui_actionCopy.setShortcut(QKeySequence('Ctrl+C'))

        self.mw.ui_actionPaste.triggered.connect(self.process_paste)
        self.mw.ui_actionPaste.setShortcut(QKeySequence('Ctrl+P'))


        # View
        self.mw.ui_actionViewNetworksDock.triggered.connect(
            self.process_view_networks_dock)
        self.mw.ui_actionViewConsoleDock.triggered.connect(
            self.process_view_console_dock)


        # Select -> Lock
        self.mw.ui_actionLockNodes.triggered.connect(
            self.process_lock_nodes)
        self.mw.ui_actionLockLinks.triggered.connect(
            self.process_lock_links)
        self.mw.ui_actionLockLabels.triggered.connect(
            self.process_lock_labels)


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
    #
    # @Slot(bool)
    # def processNewView(self):
    #     view = GraphicsView()
    #     net = self.mw.nt_manager.currentItemData
    #     if net:
    #         view.set_current_view_scene(net.scene)
    #         label = net.name
    #     else:
    #         label = "<Not selected>"
    #
    #     self.mw.sv_manager.appendView(view, label)


    # TODO: Implement Copy & Paste QGraphicsItem to the clipboard

    @Slot()
    def process_copy(self):
        print("Copy!")
        item = self.mw.nt_manager.current_item
        if not item:
            return

        net = item.data()
        scene = net.scene
        scene.clear_selection()
        brect = scene.itemsBoundingRect()
        brect.adjust(-5, -5, +10, +10)

        image = QImage(brect.width(),
                       brect.height(),
                       QImage.Format_ARGB32)

        image.fill(Qt.transparent)
        #bbrush = scene.backgroundBrush()
        #bcolor = bbrush.color()

        data = QByteArray()
        b = QBuffer(data)
        b.open(QIODevice.WriteOnly)

        svgGen = QSvgGenerator()
        svgGen.setOutputDevice(b)
        svgGen.setSize(brect.size().toSize())
        svgGen.setViewBox(QRectF(0.0, 0.0, brect.width(), brect.height()))

        painter = QPainter()
        painter.begin(svgGen)
        painter.setRenderHint(QPainter.Antialiasing)
        scene.render(painter)
        painter.end()

        mimeData = QMimeData()
        mimeData.setData("image/svg+xml", b.buffer())
        QApplication.clipboard().setMimeData(mimeData, QClipboard.Clipboard)



        # painter = QPainter(image)
        # painter.setBackgroundMode(Qt.TransparentMode)
        # painter.setRenderHint(QPainter.Antialiasing)
        # painter.setRenderHint(QPainter.HighQualityAntialiasing)
        # scene.render(painter, source=brect)
        # painter.end()
        #
        # image.save(buffer, "PNG")
        # buffer.close()
        #
        #
        # clipboard = QApplication.clipboard()
        # mimeData = QMimeData()
        # #mimeData.setImageData(image)
        # mimeData.setData("image/png", data)
        # clipboard.setMimeData(mimeData)

        #QApplication.clipboard().setImage(image, QClipboard.Clipboard)
        pass

    @Slot()
    def process_paste(self):
        print("Paste!")
        pass

    @Slot(bool)
    def process_open_network(self):

        while True:
            self.openNetworkDialog.exec()

            if self.openNetworkDialog.result() == QDialog.Rejected:
                return

            fpath = self.openNetworkDialog.fpath
            networkName = self.openNetworkDialog.network_name
            actSym = self.openNetworkDialog.act_sym
            inhSym = self.openNetworkDialog.inh_sym


            # TODO: Remove setting scene rect.
            # which prevents the automatic resizing of scene

            """
            [Qt Documentation: http://doc.qt.io/qt-5/qgraphicsscene.html]

            The scene's bounding rect is set by calling setSceneRect().
            Items can be placed at any position on the scene,
            and the size of the scene is by default unlimited.

            The scene rect is used only for internal bookkeeping,
            maintaining the scene's item index. If the scene rect is unset,
            QGraphicsScene will use the bounding area of all items,
            as returned by itemsBoundingRect(), as the scene rect.

            However, itemsBoundingRect() is a relatively time consuming
            function, as it operates by collecting positional information
            for every item on the scene. Because of this, you should always
            set the scene rect when operating on large scenes.
            """

            sceneWidth = self.openNetworkDialog.scene_width
            sceneHeight = self.openNetworkDialog.scene_height
            noLinkType = self.openNetworkDialog.no_link_type

            if noLinkType:
                actSym = None
                inhSym = None

            try:
                net = fileio.read_network(fpath,
                                          actSym, inhSym,
                                          noLinkType)
            except Exception as err:
                err_msg = "An error has occurred during opening the file.\n%s"
                self.show_error("Open a network file", err_msg % format_exc())
                continue

            break
        # end of while


        if networkName:
            net.name = networkName
        elif not net.name:
            net.name = os.path.basename(fpath)

        self.mw.sv_manager.set_current_view_scene(net.scene, net.name)
        self.mw.nt_manager.append_item(net)
        #self.mw.ct_manager.update_console_variables()

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
        print("View Networks Dock!")
        self.mw.ui_netDock.setVisible(checked)

    @Slot(bool)
    def process_view_console_dock(self, checked):
        print("View Console Dock!")
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


