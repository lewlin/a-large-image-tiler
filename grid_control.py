import sys
import numpy as np
import os
import string
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import QMouseEvent, QPixmap, QIcon, QPolygonF, QPolygon
from PyQt5.QtWidgets import QPushButton, QCheckBox, \
    QWidget, QSpinBox, QGridLayout, QLabel, QGroupBox, \
    QListWidget, QAbstractItemView, QListWidgetItem


class GridListWidgetItem(QListWidgetItem):
    """
    Provides class for items in `GridList`.
    Adds information about the grid the object refers to.
    """
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.ItemType(QListWidgetItem.UserType)  # because custom type
        flags = self.flags()
        self.setFlags(flags | Qt.ItemIsEditable)
        self.grid = None

    def set_grid(self, grid):
        self.grid = grid
        self.setIcon(QIcon('grid_icon.png'))
        # grid_num = str(len(self.parent.view.placed_grids))
        cols = str(grid.num_cols)
        rows = str(grid.num_rows)
        text = 'Grid ' + ' (' + rows + 'x' + cols + ')'
        self.setText(text)


class GridControl(QGroupBox):
    """
    Widget for controlling grids in Main Window.
    """
    """Signals"""
    sig_place_grid = pyqtSignal()
    sig_crop_region = pyqtSignal(list, float, str)
    sig_generate_rotated_image = pyqtSignal(float)

    def __init__(self, parent, title, num_rows, num_cols):
        super().__init__(parent=parent, title=title)

        # self.gc_box = QGroupBox(parent=self, title='Grid control')
        self.layout = QGridLayout()
        self.label_checkbox = QCheckBox('Toggle labels', parent=self)
        self.col_label = QLabel('Columns:', parent=self)
        self.row_label = QLabel('Rows: ', parent=self)
        self.col_spinbox = QSpinBox(parent=self,
                                       value=num_cols,
                                       maximum=26,
                                       minimum=1
                                    )
        self.row_spinbox = QSpinBox(parent=self,
                                       value=num_rows,
                                       maximum=40,
                                       minimum=1
                                    )
        self.btn_like_grid = QPushButton('I like this grid!', parent=self)
        self.grid_list = QListWidget(parent=self)
        self.btn_crop_grid = QPushButton('Crop', parent=self)
        self.btn_del_grid = QPushButton('Delete', parent=self)

        self.parent = self.parentWidget()

        self.configure_gui()
        self.configure_signals()

    def configure_gui(self):
        """
            Configure grid control
        """
        """Layout"""
        self.layout.addWidget(self.row_label, 0, 0)
        self.layout.addWidget(self.col_label, 0, 1)
        self.layout.addWidget(self.col_spinbox, 1, 1)
        self.layout.addWidget(self.row_spinbox, 1, 0)
        self.layout.addWidget(self.label_checkbox, 2, 0, 1, 2)
        self.layout.addWidget(self.btn_like_grid, 3, 0, 1, 2)
        self.layout.addWidget(self.grid_list, 4, 0, 1, 2)
        self.layout.addWidget(self.btn_crop_grid, 5, 0)
        self.layout.addWidget(self.btn_del_grid, 5, 1)
        self.setLayout(self.layout)
        self.setGeometry(0, 0, 150, 400)
        self.move(520, 90)
        """Checkbox"""
        self.label_checkbox.resize(self.label_checkbox.sizeHint())
        self.label_checkbox.setCheckState(Qt.Unchecked)
        self.label_checkbox.stateChanged.connect(self.label_checkbox_checked)
        self.label_checkbox_checked()  # update grid to default settings
        """Row/column spinboxes"""
        self.row_spinbox.valueChanged.connect(self.parent.set_num_rows)
        self.col_spinbox.valueChanged.connect(self.parent.set_num_cols)
        """I like this grid! button"""
        self.btn_like_grid.resize(self.btn_like_grid.sizeHint())
        self.btn_like_grid.setEnabled(False)
        self.btn_like_grid.clicked.connect(self.like_grid_button_clicked)
        """Grid list"""
        self.grid_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.grid_list.itemSelectionChanged.connect(self.change_selected_grid)
        self.grid_list.itemDoubleClicked.connect(self.change_grid_name)
        """Crop and del button"""
        self.btn_crop_grid.setEnabled(False)
        self.btn_crop_grid.clicked.connect(self.crop_grid_button_clicked)
        self.btn_del_grid.setEnabled(False)
        self.btn_del_grid.clicked.connect(self.del_grid_button_clicked)

    def configure_signals(self):
        self.sig_place_grid.connect(self.parent.place_grid)
        self.sig_generate_rotated_image.connect(
            self.parent.rotate_image)

    @pyqtSlot()
    def change_selected_grid(self):
        """
        Call when selected grid in `GridList` changes.
        `Crop` and `Del` are enabled, and selected grid
        changes def_color.

        Returns
        -------

        """
        grid_list = []
        for i in range(self.grid_list.count()):
            grid_list.append(self.grid_list.item(i))

        grid_list_selected = self.grid_list.selectedItems()

        for grid_item in grid_list:
            grid_item.grid.set_color_and_thickness(color=Qt.blue)

        for grid_item in grid_list_selected:
            grid_item.grid.set_color_and_thickness(color=Qt.red,
                                                   thickness=3.)

        if len(grid_list_selected) > 0:
            self.btn_crop_grid.setEnabled(True)
            self.btn_del_grid.setEnabled(True)
        else:
            self.btn_crop_grid.setEnabled(False)
            self.btn_del_grid.setEnabled(False)

    @pyqtSlot()
    def change_grid_name(self):
        item = self.grid_list.selectedItems()[0]
        self.grid_list.editItem(item)

    @pyqtSlot()
    def crop_grid_button_clicked(self):
        """
        Crop images using the selected grid in `GridList`.
        For each grid square, emit signal `sig_crop_region`,
        passing `QRectF` scaled coordinates of region to crop.

        Returns
        -------

        """

        """Collect grid information"""
        grid_item = self.grid_list.selectedItems()[0]
        image_coordinates = grid_item.grid.image_coordinates
        num_rows = grid_item.grid.num_rows
        num_cols = grid_item.grid.num_cols
        angle = grid_item.grid.phi
        alphabet = string.ascii_uppercase

        """Create directory and crop images"""
        directory = grid_item.text()
        if not os.path.exists(directory):
            os.makedirs(directory)
            """generate counter-rotated_image for cropping"""
            self.sig_generate_rotated_image.emit(-angle)

            """Crop images"""
            for ix, image_coordinate in enumerate(image_coordinates):
                """Get bg_image coordinate"""
                tl_x, tl_y = image_coordinate[0, 0]
                tl = QPointF(tl_x, tl_y)  # top left
                bl_x, bl_y = image_coordinate[0, 1]
                bl = QPointF(bl_x, bl_y)  # top right
                tr_x, tr_y = image_coordinate[1, 0]
                tr = QPointF(tr_x, tr_y)  # bottom left
                br_x, br_y = image_coordinate[1, 1]
                br = QPointF(br_x, br_y)  # bottom right
                """Find polygon to be cropped"""
                coords = [tl, bl, br, tr]
                # pol = QPolygonF(coords)
                """Determine file name"""
                col = (ix // num_rows)
                row = (ix % num_rows) + 1
                file_name = str(alphabet[col]) + str(row)
                full_path = os.path.join(directory, file_name)
                self.sig_crop_region.emit(coords, angle, full_path)
        else:
            print('Can\'t crop bg_image: folder already exist')

    @pyqtSlot()
    def del_grid_button_clicked(self):
        """
        Delete grid from `GridList`.
        Returns
        -------

        """

        """Find selected GridListItemWidget """
        grid_item = self.grid_list.selectedItems()[0]

        """Remove from GridList"""
        item_ix = self.grid_list.row(grid_item)
        self.grid_list.takeItem(item_ix)

        """Remove from scene"""
        grid_item.grid.clear_grid()

    @pyqtSlot()
    def like_grid_button_clicked(self):
        """
        Add grid to `grid_list` and emit `sig_place_grid`.

        Returns
        -------

        """

        self.btn_like_grid.setEnabled(False)

        """Add grid to placed grid widget"""
        item = GridListWidgetItem(parent=self.grid_list)
        item.set_grid(self.parent.view.current_grid)
        # TODO ItemIsEditable does not work
        # item.setFlags(Qt.ItemIsEditable)
        # item.setFlags(Qt.ItemIsSelectable)

        self.sig_place_grid.emit()

    @pyqtSlot()
    def label_checkbox_checked(self):
        """
        Enable/disable labels "A1,..,etc." in current grid.
        :return:
        """
        check_state = self.label_checkbox.checkState()
        grid = self.parent.view.current_grid

        if check_state == Qt.Checked:
            grid.label_enabled = True
        elif check_state == Qt.Unchecked:
            grid.label_enabled = False

        """Redraw grid"""
        try:
            tl, br = grid.tl_br_qpointf
        except ValueError:
            pass
        else:
            tl_x = tl.x()
            tl_y = tl.y()
            br_x = br.x()
            br_y = br.y()
            angle = grid.phi
            grid.draw_grid(tl_x, tl_y, br_x, br_y, angle)
