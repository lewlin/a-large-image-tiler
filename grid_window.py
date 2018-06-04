import sys
import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QSize, QRectF, QRect
from PyQt5.QtGui import QMouseEvent, QPixmap, QIcon
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton, \
    QWidget, QSpinBox, QGridLayout, QLabel, QGroupBox, QApplication, \
    QRadioButton, QVBoxLayout, QListWidget, QAbstractItemView,\
    QFileDialog

from adjustable_grid import AdjustableGrid
from grid_control import GridControl
from my_image import BackgroundImage


class GridView(QGraphicsView):
    """
    Provide a `QGraphicsView` to which add `AdjustableGrid`s. `GridView` is
    a child of a `parent` widget. Contain default grid properties such as `
    def_color`, `num_cols` and `num_rows`.
    """

    def __init__(self, *,
                 parent: QWidget,
                 color: Qt.GlobalColor=Qt.yellow,
                 num_cols: int=1,
                 num_rows: int=1):
        """
        Initialize a `GridView` inside a `GridWindow`, on which che user can
        draw `AdjustableGrid`s.

        Parameters
        ----------
        parent : QWidget
            Qt parent widget (expected type `GridWindow`).
        color : Qt.GlobalColor
            Grid colors. Default `Qt.yellow`
        num_cols : int
            Grid column number. Default 8.
        num_rows : int
            Grid row number. Default 12.
        """
        super().__init__(parent=parent)
        """Window properties"""
        self.setGeometry(0, 0, 500, 500)
        # self.setWindowTitle('Left click to top left grid corner')
        """W/o the following flag, mouseMove is invoked only w click+move"""
        self.setMouseTracking(True)

        """Scene"""
        self.scene = QGraphicsScene()
        self.setSceneRect(0, 0, 500, 500)
        self.setScene(self.scene)

        """Grids"""
        self.placed_grids = []
        self.color = color
        self.num_cols = num_cols
        self.num_rows = num_rows
        self.current_grid = AdjustableGrid(
            scene=self.scene,
            color=self.color,
            num_cols=self.num_cols,
            num_rows=self.num_rows
        )

        self.parent = self.parentWidget()

    def mousePressEvent(self, event: QMouseEvent):
        """Virtual function that handles mouse buttons click"""
        if self.parentWidget().mode == GridWindow.modes['grid']:
            if event.button() == Qt.LeftButton and \
                    len(self.current_grid.tl_br_qpointf) < 2:
                """If left click and grid corners are not fully specified, append 
                mouse coordinates to grid coordinates"""
                local_mouse_coordinates = self.mapToScene(event.pos())
                self.current_grid.tl_br_qpointf.append(local_mouse_coordinates)
                if len(self.current_grid.tl_br_qpointf) == 1:
                    """If one corner, add grid to scene"""
                    self.setWindowTitle('Left click to bottom right corner or '
                                        'right click to cancel')
                    self.current_grid.add_grid_to_scene()
                elif len(self.current_grid.tl_br_qpointf) == 2:
                    """If two corners, draw grid"""
                    tl_x = self.current_grid.tl_br_qpointf[0].x()
                    tl_y = self.current_grid.tl_br_qpointf[0].y()
                    br_x = self.current_grid.tl_br_qpointf[1].x()
                    br_y = self.current_grid.tl_br_qpointf[1].y()
                    self.current_grid.draw_grid(tl_x, tl_y, br_x, br_y)
                    self.setWindowTitle('Displaying grid. Right click to '
                                        'cancel grid and restart')
                    self.parent.grid_control.btn_like_grid.setEnabled(True)
                event.accept()  # prevent event propagation to parent widget
            elif event.button() == Qt.RightButton:
                """Right click reset the current grid"""
                self.current_grid.clear_grid()
                self.current_grid.init_grid_graphics()
                self.setWindowTitle('Left click to top left grid corner')
                # self.gc_btn_like_grid.setEnabled(False)
                # self.scene.addPixmap(self.rescaled_pixmap)
                event.accept()  # prevent event propagation to parent widget
            else:
                return super().mousePressEvent(event)
        else:
            """If not grid mode"""
            return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Virtual function called every time the mouse cursor is moved."""
        if self.parentWidget().mode == GridWindow.modes['grid']:
            """If GridWinow is in grid mode:"""
            if len(self.current_grid.tl_br_qpointf) == 1:
                """If only a grid corner is chosen, dynamically draw grid 
                following mouse cursor"""
                mouse_coordinates = self.mapToScene(event.pos())
                mouse_x = mouse_coordinates.x()
                mouse_y = mouse_coordinates.y()
                tl_x = self.current_grid.tl_br_qpointf[0].x()
                tl_y = self.current_grid.tl_br_qpointf[0].y()
                self.current_grid.draw_grid(tl_x, tl_y, mouse_x, mouse_y)
                event.accept()
            else:
                return super().mouseMoveEvent(event)
        else:
            """If GridWindow is not in grid mode"""
            return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        return super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        return super().mouseReleaseEvent(event)

    @pyqtSlot()
    def change_mode(self):
        """
        Switch between training mode and grid mode
        Returns
        -------

        """
        if GridWindow.modes['grid'] == self.parentWidget().mode:
            self.current_grid.setEnabled(True)
        elif GridWindow.modes['training'] == self.parentWidget().mode:
            self.current_grid.setEnabled(False)


class GridWindow(QWidget):
    """Interface/Window used to draw adjustable grids"""
    """Class attributes"""
    modes = {'grid': 0, 'training': 1}
    """Emitted when the user places a grid"""
    sig_grid_placed = pyqtSignal(np.ndarray)
    """Emitted when mode is changed"""
    sig_change_mode = pyqtSignal(int)

    def __init__(self):
        """
        Initialize the window widget.
        """
        super().__init__()
        self.setGeometry(0, 0, 700, 500)
        self.setWindowTitle('Image cropper')

        self.initial_color = Qt.darkGreen
        self.initial_no_cols = 1
        self.initial_no_rows = 1
        self.mode = GridWindow.modes['grid']

        """Initialize GridView"""
        self.view = GridView(
            parent=self,
            color=self.initial_color,
            num_rows=self.initial_no_rows,
            num_cols=self.initial_no_cols
        )

        """Initialize GridControl"""
        self.grid_control = GridControl(
            parent=self,
            title='Grid Control',
            num_rows=self.initial_no_rows,
            num_cols=self.initial_no_cols
        )

        """QImage visualized on background"""
        self.bg_image = BackgroundImage()
        # self.sig_change_mode.connect(self.view.change_mode)

        # """Mode select GUI"""
        # self.mode_box = QGroupBox(parent=self, title='Mode selection')
        # self.mode_layout = QVBoxLayout()
        # self.mode_grid_button = QRadioButton(parent=self, text='Grid mode')
        # self.mode_training_button = QRadioButton(parent=self,
        #                                          text='Training mode')

        """Open bg_image/series buttons"""
        self.open_img_button = QPushButton('Load TIFF file', parent=self)
        self.open_series_button = QPushButton('Load TIFF series', parent=self)

        self._configure_gui()
        self._configure_signals()

        self.show()
        # self.start_work()

    def _configure_gui(self):
        """
        Configure graphical objects.

        Returns
        -------

        """
        """Config. open_img_button"""
        self.open_img_button.clicked.connect(self.open_img_button_clicked)
        self.open_img_button.resize(self.open_img_button.sizeHint())
        self.open_img_button.setToolTip(
            'Load a TIFF bg_image'
        )
        self.open_img_button.move(520, 10)

        """Configure open_series_button"""
        self.open_series_button.clicked.connect(self.open_series_button_clicked)
        self.open_series_button.resize(self.open_series_button.sizeHint())
        self.open_series_button.setToolTip(
            'Load a TIFF bg_image series'
        )
        self.open_series_button.move(520, 40)
        self.open_series_button.setEnabled(False)

        # """Config. mode selection"""
        # self.mode_layout.addWidget(self.mode_grid_button)
        # self.mode_layout.addWidget(self.mode_training_button)
        # self.mode_box.setLayout(self.mode_layout)
        # self.mode_box.move(510, 10)
        # if self.mode == GridWindow.modes['grid']:
        #     self.mode_training_button.setChecked(False)
        #     self.mode_grid_button.setChecked(True)
        # elif self.mode == GridWindow.modes['training']:
        #     self.mode_training_button.setChecked(True)
        #     self.mode_grid_button.setChecked(False)
        # self.mode_training_button.clicked.connect(self.change_mode)
        # self.mode_grid_button.clicked.connect(self.change_mode)
        # self.pg_box.setLayout(self.pg_layout)
        # self.pg_box.setGeometry(0, 0, 150, 240)
        # self.pg_box.move(510, 240)

    def _configure_signals(self):
        self.grid_control.sig_crop_region.connect(self.bg_image.crop_region)

    @pyqtSlot()
    def place_grid(self):
        """
        Place grid. Compute cells coordinates and save them in grid.
        Initialize a new grid.

        Returns
        -------

        """

        """Extract grid coordinates and set cells (= images) coordinates"""
        grid_pts = self.view.current_grid.generate_grid_pts()
        self.view.current_grid.set_image_coordinates(grid_pts)
        # self.sig_grid_placed.emit(grid_pts)

        """Make grid not editable and turn it blue"""
        self.view.current_grid.make_grid_non_interactive()

        """Save grid in history"""
        self.view.placed_grids.append(self.view.current_grid)

        """Initialize new grid using view settings"""
        self.view.current_grid = AdjustableGrid(
            scene=self.view.scene,
            color=self.view.color,
            num_cols=self.view.num_cols,
            num_rows=self.view.num_rows)

    @pyqtSlot(int)
    def set_num_cols(self, num_cols: int):
        """Change column number of grid. Dynamically update a grid if is
        drawn but not displaced."""
        """Set default row number for future grids"""
        self.view.num_cols = num_cols
        if len(self.view.current_grid.tl_br_qpointf) == 2:
            """Grid has been drawn but not placed"""
            self.view.current_grid.num_cols = num_cols
            """Save current grid location"""
            phi = self.view.current_grid.phi
            tl, br = self.view.current_grid.tl_br_qpointf
            sign_x = self.view.current_grid.sign_x
            sign_y = self.view.current_grid.sign_y
            """Clear current grd"""
            self.view.current_grid.clear_grid()
            """Set previous location"""
            self.view.current_grid.tl_br_qpointf = [tl, br]
            self.view.current_grid.phi = phi
            self.view.current_grid.sign_x = sign_x
            self.view.current_grid.sign_y = sign_y
            """Draw grid and add it to scene"""
            self.view.current_grid.init_grid_graphics()
            self.view.current_grid.draw_grid(tl.x(), tl.y(), br.x(), br.y(), phi)
            self.view.current_grid.add_grid_to_scene()
        elif len(self.view.current_grid.tl_br_qpointf) == 0:
            """Grid has not been drawn"""
            self.view.current_grid.num_cols = num_cols
            self.view.current_grid.init_grid_graphics()

    @pyqtSlot(int)
    def set_num_rows(self, num_rows: int):
        """"""
        """Set default row number for future grids"""
        self.view.num_rows = num_rows
        if len(self.view.current_grid.tl_br_qpointf) == 2:
            """Grid has been drawn but not placed"""
            self.view.current_grid.num_rows = num_rows
            """Save current grid location"""
            phi = self.view.current_grid.phi
            tl, br = self.view.current_grid.tl_br_qpointf
            sign_x = self.view.current_grid.sign_x
            sign_y = self.view.current_grid.sign_y
            """Clear current grd"""
            self.view.current_grid.clear_grid()
            """Set previous location"""
            self.view.current_grid.tl_br_qpointf = [tl, br]
            self.view.current_grid.phi = phi
            self.view.current_grid.sign_x = sign_x
            self.view.current_grid.sign_y = sign_y
            """Draw grid and add it to scene"""
            self.view.current_grid.init_grid_graphics()
            self.view.current_grid.draw_grid(tl.x(), tl.y(), br.x(), br.y(), phi)
            self.view.current_grid.add_grid_to_scene()
        elif len(self.view.current_grid.tl_br_qpointf) == 0:
            """Grid has not been drawn"""
            self.view.current_grid.num_rows = num_rows
            self.view.current_grid.init_grid_graphics()

    @pyqtSlot()
    def change_mode(self):
        """Executed when a `QRadioButton `in grid control is pressed. Change
        mode in `GridWindow` and emits `sig_change_mode`."""
        if self.mode_grid_button.isChecked():
            self.mode = GridWindow.modes['grid']
            # self.gc_box.setEnabled(True)
            self.gc_box.show()
            self.sig_change_mode.emit(self.mode)
        elif self.mode_training_button.isChecked():
            self.mode = GridWindow.modes['training']
            # self.gc_box.setEnabled(False)
            self.gc_box.hide()
            self.sig_change_mode.emit(self.mode)

    @pyqtSlot()
    def open_img_button_clicked(self):
        """
        Open a file dialog that allows user to choose TIFF bg_image.
        Invoke load_image method.
        Returns
        -------

        """
        file_dialog = QFileDialog()
        file_dialog.setGeometry(10, 10, 640, 480)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        [file_name, _] = QFileDialog.getOpenFileName(
            self,
            "Choose TIFF file",
            "",
            # "Images (*.png *.xpm *.jpg);;Text files (*.txt);;",
            "TIFF Images (*.tiff *.tif)",
            options=options
        )
        file_dialog.close()

        if file_name != '':
            # self.bg_image.pixmap_from_file(file_name)
            self.bg_image.image_from_file(file_name)
            self.bg_image.show_in_scene(self.view)

    @pyqtSlot()
    def open_series_button_clicked(self):
        pass

    # TODO connect directly and avoid using pyqtSlot
    @pyqtSlot(float)
    def rotate_image(self, angle):
        self.bg_image.rotate_image(angle)
