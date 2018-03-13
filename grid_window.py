import sys
import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPixmap, QIcon
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton, \
    QWidget, QSpinBox, QGridLayout, QLabel, QGroupBox, QApplication, \
    QRadioButton, QVBoxLayout, QListWidget, QAbstractItemView, QListWidgetItem


from adjustable_grid import AdjustableGrid


class GridView(QGraphicsView):
    """Provide a `QGraphicsView` to which add `AdjustableGrid`s. `GridView` is
    a child of a `parent` widget. Contain default grid properties such as `
    color`, `num_cols` and `num_rows`."""

    def __init__(self, *,
                 parent: QWidget,
                 color: Qt.GlobalColor=Qt.yellow,
                 num_cols: int=8,
                 num_rows: int=12):
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
        self.curr_grid = AdjustableGrid(
            scene=self.scene,
            color=self.color,
            num_cols=self.num_cols,
            num_rows=self.num_rows
        )

        """Background image"""
        self.background_pixmap = QPixmap()

    def set_background(self, img_file: str):
        """UNUSED"""
        try:
            background_pixmap_unscaled = QPixmap(img_file, format='JPG')
            self.background_pixmap = \
                background_pixmap_unscaled.scaledToHeight(self.height())
        except None:
            pass  # TODO write that
        else:
            self.scene.addPixmap(self.background_pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        """Virtual function that handles mouse buttons click"""
        if self.parentWidget().mode == GridWindow.modes['grid']:
            if event.button() == Qt.LeftButton and \
                    len(self.curr_grid.tl_br_qpointf) < 2:
                """If left click and grid corners are not fully specified, append 
                mouse coordinates to grid coordinates"""
                local_mouse_coordinates = self.mapToScene(event.pos())
                self.curr_grid.tl_br_qpointf.append(local_mouse_coordinates)
                if len(self.curr_grid.tl_br_qpointf) == 1:
                    """If one corner, add grid to scene"""
                    self.setWindowTitle('Left click to bottom right corner or '
                                        'right click to cancel')
                    self.curr_grid.add_grid_to_scene()
                elif len(self.curr_grid.tl_br_qpointf) == 2:
                    """If two corners, draw grid"""
                    tl_x = self.curr_grid.tl_br_qpointf[0].x()
                    tl_y = self.curr_grid.tl_br_qpointf[0].y()
                    br_x = self.curr_grid.tl_br_qpointf[1].x()
                    br_y = self.curr_grid.tl_br_qpointf[1].y()
                    self.curr_grid.draw_grid(tl_x, tl_y, br_x, br_y)
                    self.setWindowTitle('Displaying grid. Right click to '
                                        'cancel grid and restart')
                    # self.gc_button.setEnabled(True)
                event.accept()  # prevent event propagation to parent widget
            elif event.button() == Qt.RightButton:
                """Right click reset the current grid"""
                self.curr_grid.clear_grid()
                self.curr_grid.init_grid_graphics()
                self.setWindowTitle('Left click to top left grid corner')
                # self.gc_button.setEnabled(False)
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
            if len(self.curr_grid.tl_br_qpointf) == 1:
                """If only a grid corner is chosen, dynamically draw grid 
                following mouse cursor"""
                mouse_coordinates = self.mapToScene(event.pos())
                mouse_x = mouse_coordinates.x()
                mouse_y = mouse_coordinates.y()
                tl_x = self.curr_grid.tl_br_qpointf[0].x()
                tl_y = self.curr_grid.tl_br_qpointf[0].y()
                self.curr_grid.draw_grid(tl_x, tl_y, mouse_x, mouse_y)
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
        if GridWindow.modes['grid'] == self.parentWidget().mode:
            self.curr_grid.setEnabled(True)
        elif GridWindow.modes['training'] == self.parentWidget().mode:
            self.curr_grid.setEnabled(False)


class GridWindow(QWidget):
    """Interface/Window used to draw adjustable grids"""
    """Class attributes"""
    modes = {'grid': 0, 'training': 1}
    """Emitted when the user places a grid"""
    sig_found_grid = pyqtSignal(np.ndarray)
    """Emitted when mode is changed"""
    sig_change_mode = pyqtSignal(int)

    def __init__(self):
        """
        Initialize the window widget.
        """
        super().__init__()
        self.setGeometry(0, 0, 700, 500)
        self.setWindowTitle('Grid window')

        self.initial_color = Qt.darkGreen
        self.initial_no_cols = 8
        self.initial_no_rows = 12
        self.mode = GridWindow.modes['grid']

        """Initialize GridView"""
        self.view = GridView(
            parent=self,
            color=self.initial_color,
            num_rows=self.initial_no_rows,
            num_cols=self.initial_no_cols
        )
        self.sig_change_mode.connect(self.view.change_mode)

        """Mode select GUI"""
        self.mode_box = QGroupBox(parent=self, title='Mode selection')
        self.mode_layout = QVBoxLayout()
        self.mode_grid_button = QRadioButton(parent=self, text='Grid mode')
        self.mode_training_button = QRadioButton(parent=self,
                                                 text='Training mode')

        """Grid control GUI"""
        self.gc_box = QGroupBox(parent=self, title='Grid control')
        self.gc_layout = QGridLayout()
        self.gc_col_label = QLabel('Columns:', parent=self)
        self.gc_row_label = QLabel('Rows: ', parent=self)
        self.gc_col_spinbox = QSpinBox(parent=self,
                                       value=self.initial_no_cols,
                                       maximum=26,
                                       minimum=1
                                       )
        self.gc_row_spinbox = QSpinBox(parent=self,
                                       value=self.initial_no_rows,
                                       maximum=40,
                                       minimum=1
                                       )
        self.gc_button = QPushButton('I like this grid!', parent=self)
        self.gc_list = QListWidget(parent=self)

        self.configure_gui()
        self.start_work()

    def configure_gui(self):
        """
        Configure graphical objects.

        Returns
        -------

        """

        """Config. mode selection"""
        self.mode_layout.addWidget(self.mode_grid_button)
        self.mode_layout.addWidget(self.mode_training_button)
        self.mode_box.setLayout(self.mode_layout)
        self.mode_box.move(510, 10)
        if self.mode == GridWindow.modes['grid']:
            self.mode_training_button.setChecked(False)
            self.mode_grid_button.setChecked(True)
        elif self.mode == GridWindow.modes['training']:
            self.mode_training_button.setChecked(True)
            self.mode_grid_button.setChecked(False)
        self.mode_training_button.clicked.connect(self.change_mode)
        self.mode_grid_button.clicked.connect(self.change_mode)

        """Configure grid control"""
        self.gc_layout.addWidget(self.gc_row_label, 0, 0)
        self.gc_layout.addWidget(self.gc_col_label, 0, 1)
        self.gc_layout.addWidget(self.gc_col_spinbox, 1, 1)
        self.gc_layout.addWidget(self.gc_row_spinbox, 1, 0)
        self.gc_layout.addWidget(self.gc_button, 2, 0, 1, 2)
        self.gc_layout.addWidget(self.gc_list, 3, 0, 1, 2)
        self.gc_box.setLayout(self.gc_layout)
        self.gc_box.setGeometry(0, 0, 150, 400)
        self.gc_box.move(510, 100)
        self.gc_row_spinbox.valueChanged.connect(self.set_num_rows)
        self.gc_col_spinbox.valueChanged.connect(self.set_num_cols)
        self.gc_button.resize(self.gc_button.sizeHint())
        self.gc_button.setEnabled(True)
        self.gc_button.clicked.connect(self.like_grid_button_clicked)
        self.gc_list.setSelectionMode(QAbstractItemView.SingleSelection)
        #
        # self.pg_box.setLayout(self.pg_layout)
        # self.pg_box.setGeometry(0, 0, 150, 240)
        # self.pg_box.move(510, 240)

    def start_work(self, img_file: str=None):
        """Show window w img_file in bg and allows user to draw grids"""
        # background_pixmap_unscaled = QPixmap(img_file, format='JPG')
        # self.background_pixmap = \
        #     background_pixmap_unscaled.scaledToHeight(self.height())
        # self.scene.addPixmap(self.background_pixmap)
        if img_file is not None:
            self.view.set_background(img_file)
        self.show()

    @pyqtSlot()
    def like_grid_button_clicked(self):
        """Place grid and emit its coordinates. Initialize new grid"""
        """Extract grid coordinates and emit them"""
        grid_pts = self.view.curr_grid.generate_grid_pts()
        self.sig_found_grid.emit(grid_pts)

        """Make grid not editable and turn it blue"""
        self.view.curr_grid.place_grid()

        """Save grid in history"""
        self.view.placed_grids.append(self.view.curr_grid)

        """Add grid to placed grid widget"""
        item = QListWidgetItem(parent=self.gc_list)
        item.setIcon(QIcon('grid_icon.png'))
        grid_num = str(len(self.view.placed_grids))
        cols = str(self.view.curr_grid.num_cols)
        rows = str(self.view.curr_grid.num_rows)
        text = 'Grid ' + grid_num + ' (' + rows + 'x' + cols + ')'
        item.setText(text)

        """Initialize new grid using view settings"""
        self.view.curr_grid = AdjustableGrid(
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
        if len(self.view.curr_grid.tl_br_qpointf) == 2:
            """Grid has been drawn but not placed"""
            self.view.curr_grid.num_cols = num_cols
            """Save current grid location"""
            phi = self.view.curr_grid.phi
            tl, br = self.view.curr_grid.tl_br_qpointf
            sign_x = self.view.curr_grid.sign_x
            sign_y = self.view.curr_grid.sign_y
            """Clear current grd"""
            self.view.curr_grid.clear_grid()
            """Set previous location"""
            self.view.curr_grid.tl_br_qpointf = [tl, br]
            self.view.curr_grid.phi = phi
            self.view.curr_grid.sign_x = sign_x
            self.view.curr_grid.sign_y = sign_y
            """Draw grid and add it to scene"""
            self.view.curr_grid.init_grid_graphics()
            self.view.curr_grid.draw_grid(tl.x(), tl.y(), br.x(), br.y(), phi)
            self.view.curr_grid.add_grid_to_scene()
        elif len(self.view.curr_grid.tl_br_qpointf) == 0:
            """Grid has not been drawn"""
            self.view.curr_grid.num_cols = num_cols
            self.view.curr_grid.init_grid_graphics()

    @pyqtSlot(int)
    def set_num_rows(self, num_rows: int):
        """"""
        """Set default row number for future grids"""
        self.view.num_rows = num_rows
        if len(self.view.curr_grid.tl_br_qpointf) == 2:
            """Grid has been drawn but not placed"""
            self.view.curr_grid.num_rows = num_rows
            """Save current grid location"""
            phi = self.view.curr_grid.phi
            tl, br = self.view.curr_grid.tl_br_qpointf
            sign_x = self.view.curr_grid.sign_x
            sign_y = self.view.curr_grid.sign_y
            """Clear current grd"""
            self.view.curr_grid.clear_grid()
            """Set previous location"""
            self.view.curr_grid.tl_br_qpointf = [tl, br]
            self.view.curr_grid.phi = phi
            self.view.curr_grid.sign_x = sign_x
            self.view.curr_grid.sign_y = sign_y
            """Draw grid and add it to scene"""
            self.view.curr_grid.init_grid_graphics()
            self.view.curr_grid.draw_grid(tl.x(), tl.y(), br.x(), br.y(), phi)
            self.view.curr_grid.add_grid_to_scene()
        elif len(self.view.curr_grid.tl_br_qpointf) == 0:
            """Grid has not been drawn"""
            self.view.curr_grid.num_rows = num_rows
            self.view.curr_grid.init_grid_graphics()

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


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Start Qt application
    main_window = GridWindow()
    sys.exit(app.exec_())  # Start event loop


