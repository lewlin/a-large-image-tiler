import sys
import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton, \
    QWidget, QSpinBox, QGridLayout, QLabel, QGroupBox, QApplication

from adjustable_grid import AdjustableGrid


class GridView(QGraphicsView):

    def __init__(self, *,
                 parent: QWidget,
                 color: Qt.GlobalColor=Qt.yellow,
                 no_cols: int=8,
                 no_rows: int=12):
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
        self.no_cols = no_cols
        self.no_rows = no_rows
        self.curr_grid = AdjustableGrid(
            scene=self.scene,
            color=self.color,
            no_cols=self.no_cols,
            no_rows=self.no_rows
        )
        """Background image"""
        self.background_pixmap = QPixmap()

        # self.like_grid_button.clicked.connect(self.like_grid_button_clicked)

        # self.grid_control_layout.addWidget(self.like_grid_button, 0, 0)
        # self.grid_control_layout.addLayout()
        # self.grid_control_layout.setColumnMinimumWidth(1, 100)
        # self.grid_control_layout.setRowMinimumHeight(1, 100)
        # self.grid_control_layout.addWidget(self.col_label, 0, 0)
        # self.grid_control_layout.addWidget(self.row_label, 1, 0)
        # self.grid_control_layout.addWidget(self.col_spinbox, 1, 0)
        # self.grid_control_layout.addWidget(self.row_spinbox, 1, 1)
        #

    def set_background(self, img_file: str):
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
        if event.button() == Qt.LeftButton and \
                len(self.curr_grid.tl_br_coord) < 2:
            """If left click and grid corners are not fully specified, append 
            mouse coordinates to grid coordinates"""
            local_mouse_coordinates = self.mapToScene(event.pos())
            self.curr_grid.tl_br_coord.append(local_mouse_coordinates)
            if len(self.curr_grid.tl_br_coord) == 1:
                """If one corner, add grid to scene"""
                self.setWindowTitle('Left click to bottom right corner or '
                                    'right click to cancel')
                self.curr_grid.add_grid_to_scene()
            elif len(self.curr_grid.tl_br_coord) == 2:
                """If two corners, draw grid"""
                tl_x = self.curr_grid.tl_br_coord[0].x()
                tl_y = self.curr_grid.tl_br_coord[0].y()
                br_x = self.curr_grid.tl_br_coord[1].x()
                br_y = self.curr_grid.tl_br_coord[1].y()
                self.curr_grid.draw_grid(tl_x, tl_y, br_x, br_y)
                self.setWindowTitle('Displaying grid. Right click to cancel '
                                    'grid and restart')
                # self.like_grid_button.setEnabled(True)
            event.accept()  # prevent event propagation to parent widget
        elif event.button() == Qt.RightButton:
            """Right click cancels the current grid"""
            self.curr_grid.clear_grid()
            self.setWindowTitle('Left click to top left grid corner')
            # self.like_grid_button.setEnabled(False)
            # self.scene.addPixmap(self.rescaled_pixmap)
            event.accept()  # prevent event propagation to parent widget
        else:
            return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Virtual function called every time the mouse cursor is moved."""
        if len(self.curr_grid.tl_br_coord) == 1:
            """If only a grid corner is chosen, dynamically draw grid 
            following mouse cursor"""
            mouse_coordinates = self.mapToScene(event.pos())
            mouse_x = mouse_coordinates.x()
            mouse_y = mouse_coordinates.y()
            tl_x = self.curr_grid.tl_br_coord[0].x()
            tl_y = self.curr_grid.tl_br_coord[0].y()
            self.curr_grid.draw_grid(tl_x, tl_y, mouse_x, mouse_y)
            event.accept()
        else:
            return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        return super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        return super().mouseReleaseEvent(event)


class GridWindow(QWidget):
    """Interface/Window used to draw adjustable grids"""
    """Emitted when the user places a grid"""
    sig_found_grid = pyqtSignal(np.ndarray)

    def __init__(self):
        """Window properties"""
        super().__init__()
        self.setGeometry(0, 0, 700, 500)
        self.setWindowTitle('Grid window')

        self.initial_color = Qt.darkGreen
        self.initial_no_cols = 8
        self.initial_no_rows = 12

        self.like_grid_button = QPushButton('I like this grid!', parent=self)

        self.view = GridView(
            parent=self,
            color=self.initial_color,
            no_rows=self.initial_no_rows,
            no_cols=self.initial_no_cols
        )

        """Grid control GUI"""
        self.grid_control = QGroupBox(parent=self, title='Grid control')
        self.grid_control_layout = QGridLayout()
        self.col_label = QLabel('Columns:', parent=self)
        self.row_label = QLabel('Rows: ', parent=self)

        self.col_spinbox = QSpinBox(parent=self,
                                    value=self.initial_no_cols,
                                    maximum=20,
                                    minimum=1
                                    )
        self.row_spinbox = QSpinBox(parent=self,
                                    value=self.initial_no_rows,
                                    maximum=20,
                                    minimum=1
                                    )
        self.configure_gui()
        self.start_work()

    def configure_gui(self):
        self.like_grid_button.resize(self.like_grid_button.sizeHint())
        self.like_grid_button.move(510, 120)
        self.like_grid_button.setEnabled(True)
        self.like_grid_button.clicked.connect(self.like_grid_button_clicked)

        self.grid_control_layout.addWidget(self.row_label, 0, 0)
        self.grid_control_layout.addWidget(self.col_label, 0, 1)
        self.grid_control_layout.addWidget(self.col_spinbox, 1, 1)
        self.grid_control_layout.addWidget(self.row_spinbox, 1, 0)
        self.grid_control.setLayout(self.grid_control_layout)
        self.grid_control.move(510, 10)

        self.row_spinbox.valueChanged.connect(self.set_no_rows)
        self.col_spinbox.valueChanged.connect(self.set_no_cols)

        # self.color_palette.getColor()

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
        """Initialize new grid using view settings"""
        self.view.curr_grid = AdjustableGrid(
            scene=self.view.scene,
            color=self.view.color,
            no_cols=self.view.no_cols,
            no_rows=self.view.no_rows)

    @pyqtSlot(int)
    def set_no_cols(self, no_cols: int):
        self.view.no_cols = no_cols

    @pyqtSlot(int)
    def set_no_rows(self, no_rows: int):
        self.view.no_rows = no_rows


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Start Qt application
    main_window = GridWindow()
    sys.exit(app.exec_())  # Start event loop


