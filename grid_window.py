import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton, \
    QWidget, QSpinBox, QGridLayout, QLabel, QGroupBox, QColorDialog

from movable_grid import MovableGrid


class GridView(QGraphicsView):

    def __init__(self, parent: QWidget, color: Qt.GlobalColor=Qt.yellow):
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
        self.curr_grid = MovableGrid(scene=self.scene, color=color)
        """Background image"""
        self.background_pixmap = QPixmap()

        # self.like_grid_button.clicked.connect(self.like_grid_button_clicked)

        # self.grid_control_layout.addWidget(self.like_grid_button, 0, 0)
        # self.grid_control_layout.addLayout()
        # self.grid_control_layout.setColumnMinimumWidth(1, 100)
        # self.grid_control_layout.setRowMinimumHeight(1, 100)
        # self.grid_control_layout.addWidget(self.width_label, 0, 0)
        # self.grid_control_layout.addWidget(self.height_label, 1, 0)
        # self.grid_control_layout.addWidget(self.width_spinbox, 1, 0)
        # self.grid_control_layout.addWidget(self.height_spinbox, 1, 1)
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
        self.color = Qt.darkGreen

        self.like_grid_button = QPushButton('I like this grid!', parent=self)

        self.view = GridView(parent=self, color=self.color)
        """Grid control GUI"""
        self.grid_control = QGroupBox(parent=self, title='Grid control')
        self.grid_control_layout = QGridLayout()
        self.width_label = QLabel('Width:', parent=self)
        self.height_label = QLabel('Height: ', parent=self)
        self.width_spinbox = QSpinBox(parent=self)
        self.height_spinbox = QSpinBox(parent=self)

        # self.color_palette = QColorDialog(parent=self)



        self.configure_gui()

    def configure_gui(self):
        self.like_grid_button.resize(self.like_grid_button.sizeHint())
        self.like_grid_button.move(510, 200)
        self.like_grid_button.setEnabled(True)
        self.like_grid_button.clicked.connect(self.like_grid_button_clicked)

        self.grid_control_layout.addWidget(self.height_label, 0, 0)
        self.grid_control_layout.addWidget(self.width_label, 0, 1)
        self.grid_control_layout.addWidget(self.width_spinbox, 1, 1)
        self.grid_control_layout.addWidget(self.height_spinbox, 1, 0)
        self.grid_control.setLayout(self.grid_control_layout)
        self.grid_control.move(510, 100)

        # self.color_palette.getColor()

    def start_work(self, img_file: str):
        """Show window w img_file in bg and allows user to draw grids"""
        # background_pixmap_unscaled = QPixmap(img_file, format='JPG')
        # self.background_pixmap = \
        #     background_pixmap_unscaled.scaledToHeight(self.height())
        # self.scene.addPixmap(self.background_pixmap)
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
        """Initialize a new empty grid"""
        self.view.curr_grid = MovableGrid(scene=self.view.scene, color=self.color)

