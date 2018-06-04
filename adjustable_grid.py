import numpy as np
import string
from math import isclose
from PyQt5.QtCore import Qt, QPointF, QRectF, QLineF
from PyQt5.QtGui import QPen, QPainter, QBrush
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsItem, \
    QGraphicsLineItem, QApplication, QGraphicsSceneHoverEvent, \
    QGraphicsSceneMouseEvent, QGraphicsEllipseItem, QStyleOptionGraphicsItem,\
    QGraphicsRectItem, QGraphicsTextItem


class ResizingSquare(QGraphicsRectItem):
    """Little square next to bottom right corner, used to resize the grid"""
    def __init__(self, *,
                 parent_grid: QGraphicsItem,
                 color: Qt.GlobalColor=Qt.red):
        """Initialize square with QT parent `parent_grid` and initial_color
         `initial_color`"""
        super().__init__(parent=parent_grid)
        self.setBrush(color)
        self.setAcceptHoverEvents(True)  # mouse cursor entering/exiting item

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function executed as the mouse cursor enters the disk."""
        QApplication.setOverrideCursor(Qt.CrossCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function executed when mouse cursor leaves object"""
        QApplication.setOverrideCursor(Qt.ArrowCursor)  # restore arrow cursor
        return super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Virtual function called when a mouse button is pressed"""
        self.parentItem().resize_grid()

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'): pass


class MovableDisk(QGraphicsEllipseItem):
    """Movable disk, placed to a grid corner and used to rotate the grid"""
    def __init__(self, *,
                 parent_grid: QGraphicsItem,
                 color: Qt.GlobalColor=Qt.red):
        """Initialize disk as child of `parent_grid` with initial_color
        `initial_color`"""
        super().__init__(parent=parent_grid)
        self.setBrush(color)
        self.setAcceptHoverEvents(True)  # mouse cursor entering/exiting item

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function executed as the mouse cursor enters the disk."""
        QApplication.setOverrideCursor(Qt.SizeAllCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function called when mouse cursor leaves object"""
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Virtual function called when a mouse button is pressed and the
        mouse cursor is moved"""
        """Compute old and new mouse coordinates in scene coordinates"""
        new_cursor_pos = event.scenePos()
        old_cursor_pos = event.lastScenePos()
        """Call the parent to rotate the grid """
        self.parentItem().rotate_grid(old_pos=old_cursor_pos,
                                      new_pos=new_cursor_pos,
                                      caller=self)

    """This method needs to be reimplemented"""
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    """This method needs to be reimplemented"""
    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    """This method needs to be reimplemented"""
    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'): pass


class MovableLine(QGraphicsLineItem):
    """Movable grid line. Mouse cursor changes according to permissible
    movements"""
    def __init__(self, *,
                 parent_grid: QGraphicsItem,
                 allow_horizontal_movement: bool=False,
                 allow_vertical_movement: bool=False,
                 move_all: bool=False,
                 color: Qt.GlobalColor=Qt.red):
        """Initialize line w initial_color `initial_color` and QT parent
        `parent_grid`.
        The line can be dragged by the mouse according if flags
        `allow_horizontal/vertical_movement` are `True`.
        If `move_all=True`, moving the line moves the whole grid."""
        super().__init__(parent=parent_grid)
        self.setPen(QPen(color, 2))
        self.setAcceptHoverEvents(True)  # mouse cursor entering/exiting item
        self.allow_h_mov = allow_horizontal_movement
        self.allow_v_mov = allow_vertical_movement
        self.move_all = move_all

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function called when mouse cursor enters a movable line."""
        """Change mouse cursor according to permissible movements"""
        if self.move_all is True:
            QApplication.setOverrideCursor(Qt.OpenHandCursor)
        elif self.allow_h_mov is False and self.allow_v_mov is True:
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        elif self.allow_h_mov is True and self.allow_v_mov is False:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        elif self.allow_h_mov is True and self.allow_v_mov is True:
            QApplication.setOverrideCursor(Qt.SizeAllCursor)
        elif self.allow_h_mov is False and self.allow_v_mov is False:
            QApplication.setOverrideCursor(Qt.ForbiddenCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function called when mouse leaves object"""
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Virtual function called when a mouse button is pressed and the mouse
         cursor is moved. Move the single lines or the whole grid."""
        """Compute old and new mouse coordinates in scene coordinates"""
        new_cursor_position = event.scenePos()
        old_cursor_position = event.lastScenePos()
        """Compute mouse displacement"""
        offset_x = new_cursor_position.x() - old_cursor_position.x()
        offset_y = new_cursor_position.y() - old_cursor_position.y()
        if self.move_all is False:  # if it's not a grid edge
            line_current_position = self.scenePos()
            if self.allow_v_mov is True:
                line_new_position_y = offset_y + line_current_position.y()
            else:  # allow vertical movement is False
                line_new_position_y = line_current_position.y()
            if self.allow_h_mov is True:
                line_new_position_x = offset_x + line_current_position.x()
            else:  # allow horizontal movement is False
                line_new_position_x = line_current_position.x()
            """Update line position accordingly"""
            self.setPos(QPointF(line_new_position_x, line_new_position_y))
        elif self.move_all is True:
            """Line is an edge. Update whole grid position."""
            self.parentItem().move_grid(offset_x, offset_y)

    """This method needs to be reimplemented"""
    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    """This method needs to be reimplemented"""
    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    """This method needs to be reimplemented"""
    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'): pass


class AdjustableGrid(QGraphicsItem):
    """A 12 x 8 movable/resizable grid. Grid is an abstract QT object: adding
    it to scene automatically adds the children objects (lines, disks, etc.)"""
    """Class attributes"""
    font_dist = 15  # distance (pxs) from labels to grid edge
    disk_radius = 4  # corner disk radius in pixels
    default_line_thickness = .5  # line thickness

    def __init__(self, *,
                 scene: QGraphicsScene,
                 color: Qt.GlobalColor=Qt.red,
                 num_rows: int=12,
                 num_cols: int=8):
        """Init grid. ss    et  grid def_color to `def_color` and assigns
        `QGraphicsScene scene`. Then, initialize grid graphical objects by
        calling `init_grid_graphics(). Grid is not displayed until
        `add_grid_to_scene` is called."""
        super().__init__()
        self.def_color = color
        self.scene = scene

        """Grid attributes"""
        self.tl_br_qpointf = []  # top left and bottom right corners coord.
        self.phi = 0  # CW angle between top edge and x-axis (rads) [-pi, pi]
        self.sign_x = 1  # if -1 left/right edge corresponds to right/left
        self.sign_y = 1  # if -1 top/bottom edge corresponds to bottom/top
        self.num_cols = num_cols  # grid cols
        self.num_rows = num_rows  # grid rows
        self.label_enabled = True   # show grid label

        """Grid graphical objects"""
        self.horizontal_lines = []
        self.vertical_lines = []
        self.top_edge = None
        self.bottom_edge = None
        self.left_edge = None
        self.right_edge = None
        self.square = None
        self.row_labels = []
        self.col_labels = []
        self.tl_disk = None
        self.tr_disk = None
        self.bl_disk = None
        self.br_disk = None

        """Coordinates of the images to be cropped"""
        self.image_coordinates = None

        self.init_grid_graphics()

    def init_grid_graphics(self):
        """Initialize grid graphical objects w/o displaying them."""
        """Init grid line w/o edges"""
        self.horizontal_lines = [
            MovableLine(allow_vertical_movement=False,
                        color=self.def_color,
                        parent_grid=self)
            for _ in range(self.num_rows - 1)
        ]
        self.vertical_lines = [
            MovableLine(allow_horizontal_movement=False,
                        color=self.def_color,
                        parent_grid=self)
            for _ in range(self.num_cols - 1)
        ]

        """"Grid edges (nomenclature assumes signs_x,y = 1)"""
        self.top_edge, self.bottom_edge, self.left_edge, self.right_edge = [
            MovableLine(move_all=True, parent_grid=self, color=self.def_color)
            for _ in range(4)
        ]

        """Corner disks (used to rotate the grid)"""
        self.tl_disk, self.tr_disk, self.bl_disk, self.br_disk = [
            MovableDisk(parent_grid=self, color=self.def_color)
            for _ in range(4)
        ]

        """Resizing square"""
        self.square = ResizingSquare(parent_grid=self, color=self.def_color)

        """Column labels (numerals)"""
        self.col_labels = [QGraphicsTextItem(parent=self)
                           for _ in range(self.num_rows)]
        for idx, label in enumerate(self.col_labels):
            label.setPos(0, 0)
            label.setPlainText(str(idx + 1))
            label.setDefaultTextColor(self.def_color)
            label.setVisible(False)

        """Row labels (letters)"""
        self.row_labels = [QGraphicsTextItem(parent=self)
                           for _ in range(self.num_cols)]
        alphabet = string.ascii_uppercase
        for idx, label in enumerate(self.row_labels):
            label.setPos(0, 0)
            label.setPlainText(alphabet[idx])
            label.setDefaultTextColor(self.def_color)
            label.setVisible(False)

    def paint(self, painter: QPainter,
              option: 'QStyleOptionGraphicsItem',
              widget=None):
        """Virtual function needs to be reimplemented because object is
        abstract"""
        pass

    def boundingRect(self):
        """Virtual function needs to be reimplemented because the object is
         abstract"""
        return QRectF()

    @staticmethod
    def _angle_mod(angle):
        """Helper that casts `angle` in [-pi, pi]. It is used on outcomes of
        sums or subtractions to prevent overflows."""
        angle += np.pi
        angle = angle % (2 * np.pi)
        angle -= np.pi
        return angle

    def _get_phi(self):
        """Debug helper. Return an angle that should be equal to self.phi."""
        edge = self.top_edge.line()
        delta_x = edge.x2() - edge.x1()
        delta_y = edge.y2() - edge.y1()
        angle = np.arctan2(delta_y, delta_x)
        return angle

    def clear_grid(self):
        """Remove grid from scene and reset items."""
        line_list = self.horizontal_lines + self.vertical_lines + \
                    [self.right_edge, self.left_edge] + \
                    [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        try:
            self.scene.removeItem(self)
            for line in line_list:
                line.setLine(0, 0, 0, 0)
                line.setPos(0, 0)
                line.setVisible(False)
            for disk in disk_list:
                disk.setRect(0, 0, 0, 0)
                disk.setPos(0, 0)
            for label in label_list:
                label.setPos(0, 0)
                label.setVisible(False)
            self.square.setRect(0, 0, 0, 0)
            self.square.setPos(0, 0)
        finally:
            """Reset graphical objects"""
            self.horizontal_lines = []
            self.vertical_lines = []
            self.top_edge = None
            self.bottom_edge = None
            self.left_edge = None
            self.right_edge = None
            self.square = None
            self.row_labels = []
            self.col_labels = []
            self.tl_disk = None
            self.tr_disk = None
            self.bl_disk = None
            self.br_disk = None
            """Reset grid location"""
            self.tl_br_qpointf = []
            self.sign_x = 1
            self.sign_y = 1
            self.phi = 0

    @staticmethod
    def _set_line(line: QGraphicsLineItem, x1, y1, x2, y2):
        """Helper to set `line` ends to (x1, y1) and (x2, y2)"""
        """setLine should set to 0,0 first, then call setPos. 
        Otherwise it messes the scene coordinate system."""
        line.setLine(0, 0, x2 - x1, y2 - y1)
        line.setPos(QPointF(x1, y1))

    @staticmethod
    def _set_disk(disk: QGraphicsEllipseItem, x0, y0, r):
        """Helper to center `disk` on (`x0`, `y0`) w radius `r`"""
        disk.setRect(0, 0, 2*r, 2*r)
        disk.setPos(x0 - r, y0 - r)

    @staticmethod
    def _set_square(disk: QGraphicsRectItem, x0, y0, r):
        """Helper to center `square` on `x0`, `y0` w radius `r`"""
        disk.setRect(0, 0, 2*r, 2*r)
        disk.setPos(x0 - r, y0 - r)

    def generate_grid_pts(
            self, tl_x=None, tl_y=None, br_x=None, br_y=None, angle=None
    ):
        """
        Return grid point coordinates of a grid with top
        left corner `(tl_x, tl_y)` and bottom right corner `(br_x, br_y)`,
        angled `angle` (`angle` follows same notation of `self.phi`).
        Default parameters are current grid coordinates.
        grid_pts has shape (rows+1, cols+1, 2) and is read as
        (n-th, m-th, (x, y)). Refer to the attached PDF for the notation
        used in the code.

        Parameters
        ----------
        tl_x: float
            x-coordinate of top left corner
        tl_y: float
            y-coordinate of top left corner
        br_x: float
            x-coordinate of bottom right corner
        br_y: float
            y-coordinate of bottom right corner
        angle: float
            phi angle

        Returns
        -------

        """

        """If no arguments are given use current grid position"""
        r = AdjustableGrid.disk_radius
        tl_x = self.tl_disk.x() + r if tl_x is None else tl_x
        tl_y = self.tl_disk.y() + r if tl_y is None else tl_y
        br_x = self.br_disk.x() + r if br_x is None else br_x
        br_y = self.br_disk.y() + r if br_y is None else br_y
        angle = self.phi if angle is None else angle

        """Compute angles and edge lengths"""
        tl_br_line = QLineF(tl_x, tl_y, br_x, br_y)
        tl_br_length = tl_br_line.length()
        tl_br_angle_deg = 360 - tl_br_line.angle()  # angle() is CCW in deg
        tl_br_angle_rad = tl_br_angle_deg * 2 * np.pi / 360  # convert to rad
        theta = tl_br_angle_rad - angle
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        l1 = tl_br_length * np.cos(theta)
        l2 = tl_br_length * np.sin(theta)

        """Generate grid points"""
        xs = np.array(
            [[n * l1 * cos_angle / self.num_cols -
              m * l2 * sin_angle / self.num_rows + tl_x
              for m in range(self.num_rows + 1)]
             for n in range(self.num_cols + 1)]
        )  # TODO rewrite clearly
        ys = np.array(
            [[n * l1 * sin_angle / self.num_cols +
              m * l2 * cos_angle / self.num_rows + tl_y
              for m in range(self.num_rows + 1)]
             for n in range(self.num_cols + 1)]
        )  # TODO rewrite clearly
        grid_pts = np.dstack((xs, ys))
        return grid_pts

    def draw_grid(self,
                  tl_x: float=None,
                  tl_y: float=None,
                  br_x: float=None,
                  br_y: float=None,
                  angle: float=None
    ):
        """ Draw grid given the coordinates of the top left corner, `tl_x, tl_y`
         and those of the bottom right corner `br_x, br_y`. Coordinates must be
         provided in scene coordinates. The top edge of the grid forms an angle
         `self.phi` w the x-axis.

        This function draw graphical objects but do not make direct changes
        to `QGraphicsScene`. To visualize a grid, use  method
        `add_grid_to_scene()`. Also, this method does not update the instance
        properties assigned in the constructor, like signs, phi and tl br
        coordinates.

        Refer to the attached PDF for the notation used in the code."""
        """Debug: phi difference must be zero or AssertionError"""
        phi_difference = (self.phi - self._get_phi()) % np.pi
        assert isclose(phi_difference, 0,  abs_tol=1e-4, rel_tol=1),\
            str(self.phi) + ', measured: ' + str(self._get_phi())

        """If arguments are not given, use current grid coordinates"""
        r = AdjustableGrid.disk_radius
        tl_x = self.tl_disk.x() + r if tl_x is None else tl_x
        tl_y = self.tl_disk.y() + r if tl_y is None else tl_y
        br_x = self.br_disk.x() + r if br_x is None else br_x
        br_y = self.br_disk.y() + r if br_y is None else br_y
        angle = self.phi if angle is None else angle

        """Generate horizontal and vertical lines"""
        grid_pts = self.generate_grid_pts(tl_x, tl_y, br_x, br_y, angle)
        h_lines_pts = \
            np.transpose([grid_pts[0, :], grid_pts[-1, :]], (1, 0, 2))
        v_lines_pts = \
            np.transpose([grid_pts[:, 0], grid_pts[:, -1]], (1, 0, 2))

        """Draw grid lines (except edges)"""
        for line, coordinates in zip(self.horizontal_lines, h_lines_pts[1:-1]):
            self._set_line(line, *coordinates.flatten())
        for line, coordinates in zip(self.vertical_lines, v_lines_pts[1:-1]):
            self._set_line(line, *coordinates.flatten())

        """Draw edges"""
        self._set_line(self.top_edge, *h_lines_pts[0].flatten())
        self._set_line(self.bottom_edge, *h_lines_pts[-1].flatten())
        self._set_line(self.left_edge, *v_lines_pts[0].flatten())
        self._set_line(self.right_edge, *v_lines_pts[-1].flatten())

        """Draw disks"""
        r = AdjustableGrid.disk_radius
        self._set_disk(self.tl_disk, *h_lines_pts[0, 0], r)
        self._set_disk(self.tr_disk, *h_lines_pts[0, 1], r)
        self._set_disk(self.bl_disk, *v_lines_pts[0, 1], r)
        self._set_disk(self.br_disk, *v_lines_pts[-1, 1], r)

        """Draw resizing square"""
        r = AdjustableGrid.disk_radius
        x_square, y_square = v_lines_pts[-1, 1]
        x_square += 2 * r
        y_square -= r
        self._set_square(self.square, x_square, y_square, r)

        """sign_x,y account for grid flips. e.g. if sign_y < 0, then 
        `self.top_edge` is the bottom edge. Signs account for how the user 
        places/resize grid, and do not change by rotating the grid.
        Signs are used to draw labels outside the grid."""
        if - np.pi / 2 < self.phi < np.pi / 2:
            self.sign_y = np.sign(self.bl_disk.y() - self.tl_disk.y())
            self.sign_x = np.sign(self.tr_disk.x() - self.tl_disk.x())
        else:
            self.sign_y = - np.sign(self.bl_disk.y() - self.tl_disk.y())
            self.sign_x = - np.sign(self.tr_disk.x() - self.tl_disk.x())

        """Convenience variables"""
        cos_phi = np.cos(angle)
        sin_phi = np.sin(angle)

        """Draw numbers"""
        v_edge_offset = self.left_edge.line().length() / (self.num_rows * 2)
        # assert v_edge_offset >= 0, v_edge_offset
        for label, coord, in zip(self.col_labels, h_lines_pts):
            x_c = coord[0, 0]
            y_c = coord[0, 1]
            x_b = x_c - self.sign_y * v_edge_offset * sin_phi
            y_b = y_c + self.sign_y * v_edge_offset * cos_phi
            x_d = x_b - self.sign_x * AdjustableGrid.font_dist * cos_phi
            y_d = y_b - self.sign_x * AdjustableGrid.font_dist * sin_phi
            font_offset_y = label.boundingRect().height() / 2
            font_offset_x = label.boundingRect().width() / 2
            label_y = y_d - font_offset_y
            label_x = x_d - font_offset_x
            label.setPos(label_x, label_y)  # don't need helper for these
            if self.label_enabled is True:
                label.setVisible(True)
            else:
                label.setVisible(False)

        """Draw letters"""
        h_edge_offset = self.top_edge.line().length() / (self.num_cols * 2)
        # assert h_edge_offset >= 0, h_edge_offset
        for label, coord, in zip(self.row_labels, v_lines_pts):
            x_c = coord[0, 0]
            y_c = coord[0, 1]
            x_f = x_c + self.sign_x * h_edge_offset * cos_phi
            y_f = y_c + self.sign_x * h_edge_offset * sin_phi
            x_e = x_f + self.sign_y * AdjustableGrid.font_dist * sin_phi
            y_e = y_f - self.sign_y * AdjustableGrid.font_dist * cos_phi
            font_offset_y = label.boundingRect().height() / 2
            font_offset_x = label.boundingRect().width() / 2
            label_y = y_e - font_offset_y
            label_x = x_e - font_offset_x
            label.setPos(label_x, label_y)
            if self.label_enabled is True:
                label.setVisible(True)
            else:
                label.setVisible(False)

    def add_grid_to_scene(self):
        """
        Display grid by adding all children of `AdjustableGrid` to scene.

        Returns
        -------

        """
        self.scene.addItem(self)

    def set_color_and_thickness(self, *,
                                color=None,
                                thickness=None):
        """
        Change grid def_color to `def_color`.
        Parameters
        ----------
        color: Qt.def_color

        Returns
        -------

        """

        if color is None:
            color = self.def_color
        if thickness is None:
            thickness = AdjustableGrid.default_line_thickness

        """The whole grid"""
        line_list = self.horizontal_lines + self.vertical_lines \
                    + [self.right_edge, self.left_edge] \
                    + [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        for line in line_list:
            line.setPen(QPen(color, thickness))

        for disk in disk_list:
            disk.setBrush(QBrush(color))

        for label in label_list:
            label.setDefaultTextColor(color)

    def make_grid_non_interactive(self):
        """
        Change grid def_color, disable grid mobility and mouse interaction.

        Returns
        -------

        """
        """The whole grid"""
        line_list = self.horizontal_lines + self.vertical_lines \
                    + [self.right_edge, self.left_edge] \
                    + [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        self.set_color_and_thickness(color=Qt.blue)

        for line in line_list:
            # line.setPen(QPen(Qt.blue, .5))
            line.setFlag(QGraphicsLineItem.ItemSendsGeometryChanges,
                         enabled=False)
            line.setAcceptHoverEvents(False)

        for disk in disk_list:
            # disk.setBrush(Qt.blue)
            disk.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges,
                         enabled=False)
            disk.setAcceptHoverEvents(False)
            disk.setPos(0, 0)
            disk.setRect(0, 0, 0, 0)

        """Remove labels and square"""
        for label in label_list:
            label.setPos(0, 0)
            label.setPlainText('')

        self.square.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges,
                            enabled=False)
        self.square.setAcceptHoverEvents(False)
        self.square.setRect(0, 0, 0, 0)

    def move_grid(self, offset_x, offset_y):
        """
        Move the whole grid (lines, disks, square, etc.) by spatial
        translation.

        Parameters
        ----------
        offset_x : float
            offset x coordinate.
        offset_y : float
            offset y coordinate

        Returns
        -------

        """
        line_list = self.horizontal_lines + self.vertical_lines \
                    + [self.right_edge, self.left_edge] \
                    + [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        """Update lines, disks labels, and square positions"""
        for line in line_list:
            curr_pos = line.scenePos()
            line.setTransformOriginPoint(0, 0)
            line.setPos(curr_pos.x() + offset_x, curr_pos.y() + offset_y)

        for disk in disk_list:
            curr_pos = disk.scenePos()
            disk.setTransformOriginPoint(0, 0)
            disk.setPos(curr_pos.x() + offset_x, curr_pos.y() + offset_y)

        for label in label_list:
            curr_pos = label.scenePos()
            label.setTransformOriginPoint(0, 0)
            label.setPos(curr_pos.x() + offset_x, curr_pos.y() + offset_y)

        curr_pos = self.square.scenePos()
        self.square.setTransformOriginPoint(0, 0)
        self.square.setPos(curr_pos.x() + offset_x, curr_pos.y() + offset_y)

        """Update corners position"""
        self.tl_br_qpointf = [QPointF(pt.x() + offset_x, pt.y() + offset_y)
                              for pt in self.tl_br_qpointf]

    def rotate_grid(self, *,
                    old_pos: QPointF,
                    new_pos: QPointF,
                    caller: QGraphicsEllipseItem):
        """
        Rotate the whole grid by pivoting it around the disk opposite to the
        `caller`
        disk. The angle is given by the difference of `old_pos` and `new_pos`.
        Refer to PDF file for the notation used here."

        Parameters
        ----------
        old_pos : QPointF
            old position (expected to be a mouse cursor position) of `caller`
            disk. The grid rotation angle is given by taking the difference
            between `old_pos` and `new_pos`.
        new_pos : QPointF
            new position...
        caller : QGraphicsEllipseItem
            Pivoting point is the disk opposite to `caller` disk.

        Returns
        -------

        """

        line_list = self.horizontal_lines + self.vertical_lines \
                    + [self.right_edge, self.left_edge] \
                    + [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        """Choose pivoting disk as opposite corner to caller disk"""
        if caller.scenePos() == self.tl_disk.scenePos():
            pivot_disk = self.br_disk
        elif caller.scenePos() == self.tr_disk.scenePos():
            pivot_disk = self.bl_disk
        elif caller.scenePos() == self.bl_disk.scenePos():
            pivot_disk = self.tr_disk
        elif caller.scenePos() == self.br_disk.scenePos():
            pivot_disk = self.tl_disk
        else:
            pivot_disk = None
            print('error')

        """Pivoting pt is the center of the pivoting disk. 
        scenePos() yields top left of bounding rect"""
        r = AdjustableGrid.disk_radius
        pivoting_pt = \
            pivot_disk.scenePos() + QPointF(r, r)
        pivot_x = pivoting_pt.x()
        pivot_y = pivoting_pt.y()

        """Compute angle offset between pivoting point and new/old mouse 
        coordinates"""
        old_offset_x = old_pos.x() - pivot_x
        old_offset_y = old_pos.y() - pivot_y
        new_offset_x = new_pos.x() - pivot_x
        new_offset_y = new_pos.y() - pivot_y
        old_alpha = np.arctan2(old_offset_y, old_offset_x)  # rads, [-pi, pi]
        new_alpha = np.arctan2(new_offset_y, new_offset_x)  # 0 is // to x-axis
        delta_alpha = self._angle_mod(new_alpha - old_alpha)  # CW

        """Update grid angle"""
        self.phi = self._angle_mod(self.phi + delta_alpha)

        """Update corners coordinates"""
        tl_x_pv = self.tl_br_qpointf[0].x() - pivot_x
        tl_y_pv = self.tl_br_qpointf[0].y() - pivot_y
        br_x_pv = self.tl_br_qpointf[1].x() - pivot_x
        br_y_pv = self.tl_br_qpointf[1].y() - pivot_y
        cos_delta_alpha = np.cos(delta_alpha)
        sin_delta_alpha = np.sin(delta_alpha)
        rotation_matrix = \
            np.array([[cos_delta_alpha, -sin_delta_alpha],
                      [sin_delta_alpha, cos_delta_alpha]])
        tl_x_new, tl_y_new = \
            np.dot(rotation_matrix, [tl_x_pv, tl_y_pv]) + [pivot_x, pivot_y]
        br_x_new, br_y_new = \
            np.dot(rotation_matrix, [br_x_pv, br_y_pv]) + [pivot_x, pivot_y]
        self.tl_br_qpointf = [QPointF(tl_x_new, tl_y_new),
                              QPointF(br_x_new, br_y_new)]

        """Update disks positions"""
        r = AdjustableGrid.disk_radius
        for disk in disk_list:
            curr_disk_pos = disk.scenePos() + QPointF(r, r)
            delta_x = curr_disk_pos.x() - pivoting_pt.x()
            delta_y = curr_disk_pos.y() - pivoting_pt.y()
            disk_current_angle = np.arctan2(delta_y, delta_x)
            disk_new_angle = disk_current_angle + delta_alpha
            length_to_pv_pt = QLineF(pivoting_pt, curr_disk_pos).length()
            disk_new_tl_x = length_to_pv_pt * np.cos(disk_new_angle) \
                            + pivoting_pt.x() - r
            disk_new_tl_y = length_to_pv_pt * np.sin(disk_new_angle) \
                            + pivoting_pt.y() - r
            disk.setPos(QPointF(disk_new_tl_x, disk_new_tl_y))

        """Update resizing square position"""
        r = AdjustableGrid.disk_radius
        curr_square_pos = self.square.scenePos() + QPointF(r, r)
        delta_x = curr_square_pos.x() - pivot_x
        delta_y = curr_square_pos.y() - pivot_y
        square_current_angle = np.arctan2(delta_y, delta_x)
        square_new_angle = square_current_angle + delta_alpha
        length_to_pv_pt = QLineF(pivoting_pt, curr_square_pos).length()
        square_new_tl_x = length_to_pv_pt * np.cos(square_new_angle) \
                          + pivot_x - r
        square_new_tl_y = length_to_pv_pt * np.sin(square_new_angle) \
                          + pivot_y - r
        self.square.setPos(QPointF(square_new_tl_x, square_new_tl_y))

        """Update lines positions"""
        for line in line_list:
            line_loc = line.line()  # in local coordinates
            line_offset = line.scenePos()
            line_pt1 = line_loc.p1() + line_offset
            line_pt2 = line_loc.p2() + line_offset
            delta_y1 = line_pt1.y() - pivot_y
            delta_x1 = line_pt1.x() - pivot_x
            delta_y2 = line_pt2.y() - pivot_y
            delta_x2 = line_pt2.x() - pivot_x
            line_angle1_new = np.arctan2(delta_y1, delta_x1) + delta_alpha
            line_angle2_new = np.arctan2(delta_y2, delta_x2) + delta_alpha
            length_to_pv_pt_1 = QLineF(pivoting_pt, line_pt1).length()
            length_to_pv_pt_2 = QLineF(pivoting_pt, line_pt2).length()
            line_x1 = length_to_pv_pt_1 * np.cos(line_angle1_new) + pivot_x
            line_y1 = length_to_pv_pt_1 * np.sin(line_angle1_new) + pivot_y
            line_x2 = length_to_pv_pt_2 * np.cos(line_angle2_new) + pivot_x
            line_y2 = length_to_pv_pt_2 * np.sin(line_angle2_new) + pivot_y
            self._set_line(line, line_x1, line_y1, line_x2, line_y2)

        """Update labels positions"""
        for label in label_list:
            """The label center coordinates are x_d, y_d (see fig.)"""
            curr_label_pos = label.scenePos()
            font_offset_y = label.boundingRect().height() / 2
            font_offset_x = label.boundingRect().width() / 2
            assert(font_offset_x > 0 and font_offset_y > 0)
            x_d = curr_label_pos.x() + font_offset_x
            y_d = curr_label_pos.y() + font_offset_y
            """delta is the vector from pivoting pt to font center"""
            delta_x = x_d - pivot_x
            delta_y = y_d - pivot_y
            delta = np.sqrt((delta_x ** 2) + (delta_y ** 2))
            label_curr_angle = np.arctan2(delta_y, delta_x)
            label_new_angle = label_curr_angle + delta_alpha
            x_d = delta * np.cos(label_new_angle) + pivot_x
            y_d = delta * np.sin(label_new_angle) + pivot_y
            label_new_tl_x = x_d - font_offset_x
            label_new_tl_y = y_d - font_offset_y
            label.setPos(QPointF(label_new_tl_x, label_new_tl_y))

    def resize_grid(self):
        """Take out coordinate of bottom right corner. This calls virtual function
        mouseMoveEvent from GridWindow"""
        self.tl_br_qpointf = self.tl_br_qpointf[:-1]

    @staticmethod
    def _duplicate_array(array: np.ndarray):
        """
        Helper that takes a NumPy array and duplicates each element except
        the endpoint. *e.g.*  if `array  = [1, 2, 3, 4]`, the helper returns
        `[1, 2, 2, 3, 3, 4]`. The method only process the first array
        dimension.

        Parameters
        ----------
        array: NumPy Array
            Array to be duplicated

        Returns
        -------
        Duplicated Numpy array
        """

        mask = np.repeat(2, len(array) - 2)
        mask = np.insert(mask, 0, 1)
        mask = np.append(mask, 1)
        """Mask is [1, 2, 2....2, 1]"""
        assert len(mask) == len(array)
        duplicated_array = np.repeat(array, mask, axis=0)
        return duplicated_array

    def set_image_coordinates(self, grid_pts=None):
        """
        Use grid coordinates `grid_pts` to set `self.image_coordinates`
        to the list of coordinates of grid cells. `self.image_coordinates` is
        a list of length equal to the number of cells in the grid. Each cell
        has coordinates in the form: `[[tl_x, tl_y], [bl_x, bl_y]],
        [[tr_x, tr_y], [br_x, br_y]]`. Cells are ordered as in
        `cell_order_example.png` (fig. assumes phi = 0).

        Parameters
        ----------
        grid_pts:
            Grid coordinates.

        Returns
        -------

        """
        n_rows = self.num_rows  # 12
        n_cols = self.num_cols   # 8
        assert grid_pts.shape == (n_cols + 1, n_rows + 1, 2)

        """Duplicate columns and rows except end point to cast grid coordinates
        into bg_image coordinates."""
        pts_2x_cols = self._duplicate_array(grid_pts)
        new_n_cols = (n_cols-1) * 2 + 2
        assert pts_2x_cols.shape == (new_n_cols, n_rows + 1, 2)
        pts_2x_cols_t = np.transpose(pts_2x_cols, (1, 0, 2))
        pts_2x_cols_rows_t = self._duplicate_array(pts_2x_cols_t)
        pts_2x_cols_rows = np.transpose(pts_2x_cols_rows_t, (1, 0, 2))
        assert pts_2x_cols_rows.shape == (n_cols * 2, n_rows * 2, 2), \
            'shape found {}'.format(pts_2x_cols_rows.shape)

        """Generate bg_image coordinates"""
        cols = int(pts_2x_cols_rows.shape[0] / 2)  # 8
        rows = int(pts_2x_cols_rows.shape[1] / 2)  # 12
        img_coordinates = np.array([
            pts_2x_cols_rows[2*n:2*n+2, 2*m:2*m+2]  # could use list(zip(...))
            for n in range(cols) for m in range(rows)
        ])
        assert img_coordinates.shape == (n_rows * n_cols, 2, 2, 2)
        self.image_coordinates = img_coordinates

        # print(self.image_coordinates)

    def set_line_thickness(self):
        pass