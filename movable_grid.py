import sys
import itertools
import numpy as np
from math import isclose, fmod
from PyQt5.QtCore import Qt, pyqtSlot, QPointF, QRectF, QLineF
from PyQt5.QtGui import QMouseEvent, QPen, QPainter
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsLineItem, QApplication,\
    QGraphicsSceneHoverEvent, QPushButton, QGraphicsSceneMouseEvent, QGraphicsEllipseItem, QStyleOptionGraphicsItem,\
    QGraphicsRectItem, QGraphicsTextItem


class ResizingSquare(QGraphicsRectItem):
    """Little square that appears next to bottom right corner, used to resize the grid"""
    def __init__(self, parent_grid: QGraphicsItem, color: Qt.GlobalColor=Qt.red):
        """Initialize square as parent of parent_grid with color color"""
        super().__init__(parent=parent_grid)
        self.setBrush(color)
        self.setAcceptHoverEvents(True)  # hover events include mouse cursor entering/exiting item

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function executed as the mouse cursor enters the disk."""
        QApplication.setOverrideCursor(Qt.CrossCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Restore cursor when mouse leaves movable line object"""
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Virtual function called when a mouse button is pressed and the mouse cursor is moved"""
        self.parentItem().resize_grid()

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'): pass


class MovableDisk(QGraphicsEllipseItem):
    """A movable disk, placed to a grid corner and used to rotate the grid"""
    def __init__(self, parent_grid: QGraphicsItem, color: Qt.GlobalColor=Qt.red):
        """Initialize disk as parent of parent_grid with color color"""
        super().__init__(parent=parent_grid)
        self.setBrush(color)
        self.setAcceptHoverEvents(True)  # hover events include mouse cursor entering/exiting item

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Virtual function executed as the mouse cursor enters the disk."""
        QApplication.setOverrideCursor(Qt.SizeAllCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Restore cursor when mouse leaves movable line object"""
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Virtual function called when a mouse button is pressed and the mouse cursor is moved"""
        """Compute old and new mouse coordinates in scene coordinates"""
        new_cursor_pos = event.scenePos()
        old_cursor_pos = event.lastScenePos()
        """Call the parent and rotate the grid according to mouse cursor position"""
        self.parentItem().rotate_grid(old_cursor_pos, new_cursor_pos, self)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'): pass


class MovableLine(QGraphicsLineItem):
    """A movable grid line. Mouse cursor changes according to permissible movements"""
    def __init__(self, parent_grid: QGraphicsItem, allow_horizontal_movement: bool=False,
                 allow_vertical_movement: bool=False, move_all: bool=False, color: Qt.GlobalColor=Qt.red):
        """Initialize line"""
        super().__init__(parent=parent_grid)
        self.setPen(QPen(color, 2))
        self.setAcceptHoverEvents(True)  # hover events include mouse cursor entering/exiting item
        self.allow_horizontal_movement = allow_horizontal_movement
        self.allow_vertical_movement = allow_vertical_movement
        self.move_all = move_all  # If True, dragging the line will move the whole grid.

    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """When mouse cursor enters a movable line, change cursor according to permissible movements"""
        if self.move_all is True:
            QApplication.setOverrideCursor(Qt.OpenHandCursor)
        elif self.allow_horizontal_movement is False and self.allow_vertical_movement is True:
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        elif self.allow_horizontal_movement is True and self.allow_vertical_movement is False:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        elif self.allow_horizontal_movement is True and self.allow_vertical_movement is True:
            QApplication.setOverrideCursor(Qt.SizeAllCursor)
        elif self.allow_horizontal_movement is False and self.allow_vertical_movement is False:
            QApplication.setOverrideCursor(Qt.ForbiddenCursor)
        return super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent'):
        """Restore cursor when mouse leaves movable line object"""
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return super().hoverLeaveEvent(event)

    def mouseMoveEvent(self, event: 'QGraphicsSceneMouseEvent'):
        """Virtual function called when a mouse button is pressed and the mouse cursor is moved.
        It is used to move the single lines or the whole grid"""
        """Compute old and new mouse coordinates in scene coordinates"""
        new_cursor_position = event.scenePos()
        old_cursor_position = event.lastScenePos()
        """Compute mouse displacement"""
        offset_x = new_cursor_position.x() - old_cursor_position.x()
        offset_y = new_cursor_position.y() - old_cursor_position.y()
        if self.move_all is False:  # if it's not a grid edge
            line_current_position = self.scenePos()
            if self.allow_vertical_movement is True:
                line_new_position_y = offset_y + line_current_position.y()
            else:  # allow vertical movement is False
                line_new_position_y = line_current_position.y()
            if self.allow_horizontal_movement is True:
                line_new_position_x = offset_x + line_current_position.x()
            else:  # allow horizontal movement is False
                line_new_position_x = line_current_position.x()
            """Update line position accordingly"""
            self.setPos(QPointF(line_new_position_x, line_new_position_y))
        elif self.move_all is True:
            """Line is an edge. Update whole grid position."""
            self.parentItem().move_grid(offset_x, offset_y)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mouseDoubleClickEvent(self, event: 'QGraphicsSceneMouseEvent'): pass

    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent'): pass


class MovableGrid(QGraphicsItem):
    """A 12 x 8 movable/adjustable grid. Grid is an abstract object: adding it to scene automatically adds
    the children objects (lines, disks, etc.)"""
    def __init__(self, scene: QGraphicsScene, color: Qt.GlobalColor=Qt.red):
        """Init grid and children objects"""
        super().__init__()
        """Initialize a grid of color color on scene scene"""
        self.color = color
        self.scene = scene
        self.corners_coordinates = []  # top left and bottom right corners coordinates
        self.phi = 0  # CW angle between top edge and x-axis (rads) [-pi, pi]
        self.sign_x = 1  # if -1 left/right edge corresponds to right/left
        self.sign_y = 1  # if -1 top/bottom edge corresponds to bottom/top
        """Grid has 11 horizontal lines and 7 vertical lines"""
        self.horizontal_lines = [MovableLine(allow_vertical_movement=False, color=color, parent_grid=self)
                                 for _ in itertools.repeat(None, 11)]
        self.vertical_lines = [MovableLine(allow_horizontal_movement=False, color=color, parent_grid=self)
                               for _ in itertools.repeat(None, 7)]
        """"Grid edges (nomenclature assumes that user chooses top left corner first)"""
        self.top_edge = MovableLine(move_all=True, parent_grid=self, color=color)
        self.bottom_edge = MovableLine(move_all=True, parent_grid=self, color=color)
        self.left_edge = MovableLine(move_all=True, parent_grid=self, color=color)
        self.right_edge = MovableLine(move_all=True, parent_grid=self, color=color)
        """Corner disks (used to rotate the grid)"""
        self.disk_radius = 4  # in pxs
        self.tl_disk = MovableDisk(parent_grid=self, color=color)
        self.tr_disk = MovableDisk(parent_grid=self, color=color)
        self.bl_disk = MovableDisk(parent_grid=self, color=color)
        self.br_disk = MovableDisk(parent_grid=self, color=color)
        """Resizing square"""
        self.square = ResizingSquare(parent_grid=self, color=color)
        """Grid labels"""
        self.font_dist = 15  # distance (pxs) from labels to grid
        self.col_labels = [QGraphicsTextItem(parent=self) for _ in range(12)]
        for idx, label in enumerate(self.col_labels):
            label.setPos(0, 0)
            label.setPlainText(str(idx + 1))
            label.setDefaultTextColor(Qt.red)
            label.setVisible(False)
        self.row_labels = [QGraphicsTextItem(parent=self) for _ in range(8)]
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for idx, label in enumerate(self.row_labels):
            label.setPos(0, 0)
            label.setPlainText(alphabet[idx])
            label.setDefaultTextColor(Qt.red)
            label.setVisible(False)

    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget=None):
        """This function needs to be reimplemented because the object is abstract"""
        pass

    def boundingRect(self):
        """This function needs to be reimplemented because the object is abstract"""
        return QRectF()

    def angle_mod(self, angle):
        """Takes angle and returns it in [-pi, pi]. It is used when angles defined [-pi , pi]
        are summed or subtrated"""
        angle += np.pi
        angle = angle % (2 * np.pi)
        angle -= np.pi
        return angle

    def get_phi(self):
        """Debug function used to ensure that self.phi corresponds to angle between top edge and x-axis"""
        edge = self.top_edge.line()
        delta_x = edge.x2() - edge.x1()
        delta_y = edge.y2() - edge.y1()
        angle = np.arctan2(delta_y, delta_x)
        return angle

    def clear_grid(self):
        """Remove grid from scene and reset items"""
        line_list = self.horizontal_lines + self.vertical_lines + [self.right_edge, self.left_edge] \
                    + [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        try:
            self.scene.removeItem(self)
        finally:
            for line in line_list:
                line.setLine(0, 0, 0, 0)
                line.setPos(0, 0)
            for disk in disk_list:
                disk.setRect(0, 0, 0, 0)
                disk.setPos(0, 0)
            for label in label_list:
                label.setPos(0, 0)
                label.setVisible(False)
            self.square.setRect(0, 0, 0, 0)
            self.square.setPos(0, 0)
            self.corners_coordinates = []
            self.phi = 0

    def set_line(self, line: QGraphicsLineItem, x1, y1, x2, y2):
        """Use this function to set line position. Other ways might mess up scene coordinates system"""
        line.setLine(0, 0, x2 - x1, y2 - y1)
        line.setPos(QPointF(x1, y1))

    def set_disk(self, disk: QGraphicsEllipseItem, x0, y0, r):
        """Set disk or square centered on x0, y0 w radius r accounting for scenePos coordinate system"""
        disk.setRect(0, 0, 2*r, 2*r)
        disk.setPos(x0 - r, y0 - r)

    def set_square(self, disk: QGraphicsRectItem, x0, y0, r):
        """Set disk or square centered on x0, y0 w radius r accounting for scenePos coordinate system"""
        disk.setRect(0, 0, 2*r, 2*r)
        disk.setPos(x0 - r, y0 - r)

    def draw_grid(self, tl_x, tl_y, br_x, br_y):
        """ Draw a regular grid given the coordinates of the two corners, angled by self.angle.
        This function manipulates line positions but do not make direct changes to scene.
        Refer to the attached PDF for the notation used"""
        """Check phi"""
        assert isclose((self.phi - self.get_phi()) % np.pi, 0, abs_tol=1e-4, rel_tol=1),\
            str(self.phi) + ', measured: ' + str(self.get_phi())

        """Compute angles and distances"""
        tl_br_line = QLineF(tl_x, tl_y, br_x, br_y)
        d = tl_br_line.length()
        tl_br_angle_deg = 360 - tl_br_line.angle()  # angle() returns counterclockwise angles in deg
        tl_br_angle_rad = tl_br_angle_deg * 2 * np.pi / 360  # convert to rad
        theta = tl_br_angle_rad - self.phi
        cos_phi = np.cos(self.phi)
        sin_phi = np.sin(self.phi)
        l1 = d * np.cos(theta)
        l2 = d * np.sin(theta)

        """Generate grid points"""
        xs2 = np.array([[n * l1 * cos_phi / 8 - m * l2 * sin_phi / 12 + tl_x for m in range(13)] for n in range(9)])
        ys2 = np.array([[n * l1 * sin_phi / 8 + m * l2 * cos_phi / 12 + tl_y for m in range(13)] for n in range(9)])
        grid_pts = np.dstack((xs2, ys2))  # grid_pts.shape = (9, 13, 2)
        horizontal_lines_pts = np.transpose([grid_pts[0, :], grid_pts[-1, :]], (1, 0, 2))
        vertical_lines_pts = np.transpose([grid_pts[:, 0], grid_pts[:, -1]], (1, 0, 2))

        """Draw grid lines (except edges)"""
        for line, coordinates in zip(self.horizontal_lines, horizontal_lines_pts[1:-1]):
            self.set_line(line, *coordinates.flatten())
        for line, coordinates in zip(self.vertical_lines, vertical_lines_pts[1:-1]):
            self.set_line(line, *coordinates.flatten())

        """Draw edges"""
        self.set_line(self.top_edge, *horizontal_lines_pts[0].flatten())
        self.set_line(self.bottom_edge, *horizontal_lines_pts[-1].flatten())
        self.set_line(self.left_edge, *vertical_lines_pts[0].flatten())
        self.set_line(self.right_edge, *vertical_lines_pts[-1].flatten())

        """Draw disks"""
        self.set_disk(self.tl_disk, *horizontal_lines_pts[0, 0], self.disk_radius)
        self.set_disk(self.tr_disk, *horizontal_lines_pts[0, 1], self.disk_radius)
        self.set_disk(self.bl_disk, *vertical_lines_pts[0, 1], self.disk_radius)
        self.set_disk(self.br_disk, *vertical_lines_pts[-1, 1], self.disk_radius)

        """Draw resizing square"""
        x_square, y_square = vertical_lines_pts[-1, 1]
        x_square += 2 * self.disk_radius
        y_square -= self.disk_radius
        self.set_square(self.square, x_square, y_square, self.disk_radius)

        """sign_x,y account for grid flips. e.g. if sign_y < 0 then top edge is bottom.
        Signs account for how the user places/resize grid and is independent of phi.
        Signs are used to draw labels outside the grid."""
        if - np.pi / 2 < self.phi < np.pi / 2:
            self.sign_y = np.sign(self.bl_disk.y() - self.tl_disk.y())
            self.sign_x = np.sign(self.tr_disk.x() - self.tl_disk.x())
        else:
            self.sign_y = - np.sign(self.bl_disk.y() - self.tl_disk.y())
            self.sign_x = - np.sign(self.tr_disk.x() - self.tl_disk.x())

        """Draw numbers"""
        v_edge_offset = self.left_edge.line().length() / 24  # 24 = 12 x 2
        assert v_edge_offset >= 0, v_edge_offset
        for label, coord, in zip(self.col_labels, horizontal_lines_pts):
            x_c = coord[0, 0]
            y_c = coord[0, 1]
            x_b = x_c - self.sign_y * v_edge_offset * sin_phi
            y_b = y_c + self.sign_y * v_edge_offset * cos_phi
            x_d = x_b - self.sign_x * self.font_dist * cos_phi
            y_d = y_b - self.sign_x * self.font_dist * sin_phi
            font_offset_y = label.boundingRect().height() / 2
            font_offset_x = label.boundingRect().width() / 2
            label_y = y_d - font_offset_y
            label_x = x_d - font_offset_x
            label.setPos(label_x, label_y)
            label.setVisible(True)

        """Draw letters"""
        h_edge_offset = self.top_edge.line().length() / 16  # 16 = 8 x 2
        assert h_edge_offset >= 0, h_edge_offset
        for label, coord, in zip(self.row_labels, vertical_lines_pts):
            x_c = coord[0, 0]
            y_c = coord[0, 1]
            x_f = x_c + self.sign_x * h_edge_offset * cos_phi
            y_f = y_c + self.sign_x * h_edge_offset * sin_phi
            x_e = x_f + self.sign_y * self.font_dist * sin_phi
            y_e = y_f - self.sign_y * self.font_dist * cos_phi
            font_offset_y = label.boundingRect().height() / 2
            font_offset_x = label.boundingRect().width() / 2
            label_y = y_e - font_offset_y
            label_x = x_e - font_offset_x
            label.setPos(label_x, label_y)
            label.setVisible(True)

    def add_grid_to_scene(self):
        """Add all children items of MovableGrid to scene"""
        self.scene.addItem(self)

    def set_immutable(self):
        """Change grid color, disable grid mobility and mouse interaction"""
        line_list = self.horizontal_lines + self.vertical_lines + [self.right_edge, self.left_edge] \
                    + [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        for line in line_list:
            line.setPen(QPen(Qt.blue, 2))
            line.setFlag(QGraphicsLineItem.ItemSendsGeometryChanges, enabled=False)
            line.setAcceptHoverEvents(False)

        for disk in disk_list:
            disk.setBrush(Qt.blue)
            disk.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges, enabled=False)
            disk.setAcceptHoverEvents(False)

        for label in label_list:
            label.setPos(0, 0)
            label.setPlainText('')

        self.square.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges, enabled=False)
        self.square.setAcceptHoverEvents(False)
        self.square.setRect(0, 0, 0, 0)

    def move_grid(self, offset_x, offset_y):
        """Move the whole grid by offset"""
        line_list = self.horizontal_lines + self.vertical_lines + [self.right_edge, self.left_edge] \
                    + [self.top_edge, self.bottom_edge]

        disk_list = [self.tl_disk, self.tr_disk, self.br_disk, self.bl_disk]

        label_list = self.row_labels + self.col_labels

        """Update lines, disks labels, and square positions"""
        for line in line_list:
            current_position = line.scenePos()
            line.setTransformOriginPoint(0, 0)
            line.setPos(current_position.x() + offset_x, current_position.y() + offset_y)

        for disk in disk_list:
            current_position = disk.scenePos()
            disk.setTransformOriginPoint(0, 0)
            disk.setPos(current_position.x() + offset_x, current_position.y() + offset_y)

        for label in label_list:
            current_position = label.scenePos()
            label.setTransformOriginPoint(0, 0)
            label.setPos(current_position.x() + offset_x, current_position.y() + offset_y)

        current_position = self.square.scenePos()
        self.square.setTransformOriginPoint(0, 0)
        self.square.setPos(current_position.x() + offset_x, current_position.y() + offset_y)

        """Update corners position"""
        self.corners_coordinates = [QPointF(pt.x() + offset_x, pt.y() + offset_y)
                                    for pt in self.corners_coordinates]

    def rotate_grid(self, old_mouse_pos: QPointF, new_mouse_pos: QPointF, caller: QGraphicsEllipseItem):
        """Rotate grid by pivoting it around the disk opposite to the caller disk. The angle follows
        the mouse cursor. Refer to PDF file for the notation used here."""
        line_list = self.horizontal_lines + self.vertical_lines + [self.right_edge, self.left_edge] \
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

        """Pivoting pt is the center of the pivoting disk. scenePos() yields top left of bounding rect"""
        pivoting_pt = pivot_disk.scenePos() + QPointF(self.disk_radius, self.disk_radius)

        """Compute angle offset between pivoting point and new/old mouse coordinates"""
        old_offset_x = old_mouse_pos.x() - pivoting_pt.x()
        old_offset_y = old_mouse_pos.y() - pivoting_pt.y()
        new_offset_x = new_mouse_pos.x() - pivoting_pt.x()
        new_offset_y = new_mouse_pos.y() - pivoting_pt.y()
        old_alpha = np.arctan2(old_offset_y, old_offset_x)  # rads, [-pi, pi]
        new_alpha = np.arctan2(new_offset_y, new_offset_x)  # 0 is // to x-axis
        delta_alpha = self.angle_mod(new_alpha - old_alpha)  # CW

        """Update grid angle"""
        self.phi = self.angle_mod(self.phi + delta_alpha)

        """Update corners coordinates"""
        tl_x_pv = self.corners_coordinates[0].x() - pivoting_pt.x()
        tl_y_pv = self.corners_coordinates[0].y() - pivoting_pt.y()
        br_x_pv = self.corners_coordinates[1].x() - pivoting_pt.x()
        br_y_pv = self.corners_coordinates[1].y() - pivoting_pt.y()
        cos_delta_alpha = np.cos(delta_alpha)
        sin_delta_alpha = np.sin(delta_alpha)
        rotation_matrix = np.array([[cos_delta_alpha, -sin_delta_alpha],[sin_delta_alpha, cos_delta_alpha]])
        tl_x_new, tl_y_new = np.dot(rotation_matrix, [tl_x_pv, tl_y_pv]) + [pivoting_pt.x(), pivoting_pt.y()]
        br_x_new, br_y_new = np.dot(rotation_matrix, [br_x_pv, br_y_pv]) + [pivoting_pt.x(), pivoting_pt.y()]
        self.corners_coordinates = [QPointF(tl_x_new, tl_y_new), QPointF(br_x_new, br_y_new)]

        """Update disks positions"""
        for disk in disk_list:
            current_disk_pos = disk.scenePos() + QPointF(self.disk_radius, self.disk_radius)
            delta_x = current_disk_pos.x() - pivoting_pt.x()
            delta_y = current_disk_pos.y() - pivoting_pt.y()
            disk_current_angle = np.arctan2(delta_y, delta_x)
            disk_new_angle = disk_current_angle + delta_alpha
            length_to_pv_pt = QLineF(pivoting_pt, current_disk_pos).length()
            disk_new_tl_x = length_to_pv_pt * np.cos(disk_new_angle) + pivoting_pt.x() - self.disk_radius
            disk_new_tl_y = length_to_pv_pt * np.sin(disk_new_angle) + pivoting_pt.y() - self.disk_radius
            disk.setPos(QPointF(disk_new_tl_x, disk_new_tl_y))  # use set disk instead?

        """Update resizing square position"""
        current_square_pos = self.square.scenePos() + QPointF(self.disk_radius, self.disk_radius)
        delta_x = current_square_pos.x() - pivoting_pt.x()
        delta_y = current_square_pos.y() - pivoting_pt.y()
        square_current_angle = np.arctan2(delta_y, delta_x)
        square_new_angle = square_current_angle + delta_alpha
        length_to_pv_pt = QLineF(pivoting_pt, current_square_pos).length()
        square_new_tl_x = length_to_pv_pt * np.cos(square_new_angle) + pivoting_pt.x() - self.disk_radius
        square_new_tl_y = length_to_pv_pt * np.sin(square_new_angle) + pivoting_pt.y() - self.disk_radius
        self.square.setPos(QPointF(square_new_tl_x, square_new_tl_y))  # use set disk instead?

        """Update lines positions"""
        for line in line_list:
            line_loc = line.line()  # in local coordinates
            line_offset = line.scenePos()
            line_pt1 = line_loc.p1() + line_offset
            line_pt2 = line_loc.p2() + line_offset
            delta_y1 = line_pt1.y() - pivoting_pt.y()
            delta_x1 = line_pt1.x() - pivoting_pt.x()
            delta_y2 = line_pt2.y() - pivoting_pt.y()
            delta_x2 = line_pt2.x() - pivoting_pt.x()
            line_angle1_new = np.arctan2(delta_y1, delta_x1) + delta_alpha
            line_angle2_new = np.arctan2(delta_y2, delta_x2) + delta_alpha
            length_to_pv_pt_1 = QLineF(pivoting_pt, line_pt1).length()
            length_to_pv_pt_2 = QLineF(pivoting_pt, line_pt2).length()
            line_new_x1 = length_to_pv_pt_1 * np.cos(line_angle1_new) + pivoting_pt.x()
            line_new_y1 = length_to_pv_pt_1 * np.sin(line_angle1_new) + pivoting_pt.y()
            line_new_x2 = length_to_pv_pt_2 * np.cos(line_angle2_new) + pivoting_pt.x()
            line_new_y2 = length_to_pv_pt_2 * np.sin(line_angle2_new) + pivoting_pt.y()
            self.set_line(line, line_new_x1, line_new_y1, line_new_x2, line_new_y2)

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
            delta_x = x_d - pivoting_pt.x()
            delta_y = y_d - pivoting_pt.y()
            delta = np.sqrt((delta_x ** 2) + (delta_y ** 2))
            label_curr_angle = np.arctan2(delta_y, delta_x)
            label_new_angle = label_curr_angle + delta_alpha
            x_d = delta * np.cos(label_new_angle) + pivoting_pt.x()
            y_d = delta * np.sin(label_new_angle) + pivoting_pt.y()
            label_new_tl_x = x_d - font_offset_x
            label_new_tl_y = y_d - font_offset_y
            label.setPos(QPointF(label_new_tl_x, label_new_tl_y))

            """Check phi"""
            assert isclose(self.phi, self.get_phi(), rel_tol=1e-5), str(self.phi) + ', measured: ' + str(self.get_phi())

    def resize_grid(self):
        """Take out coordinate of bottom right corner. This calls virtual function
        mouseMoveEvent from GridWindow"""
        self.corners_coordinates = self.corners_coordinates[:-1]


class GridWindow(QGraphicsView):
    """Interface/Window used to draw adjustable grids"""
    def __init__(self):
        super().__init__()
        """Window properties"""
        self.setGeometry(0, 0, 500, 500)
        self.setWindowTitle('Left click to top left grid corner')
        self.setMouseTracking(True)  # otherwise mouseMove will respond only on mouse clicks
        """Scene"""
        self.scene = QGraphicsScene()
        self.setSceneRect(0, 0, 500, 500)
        self.setScene(self.scene)
        """Buttons"""
        self.like_grid_button = QPushButton('I like this grid!', self)
        self.like_grid_button.resize(self.like_grid_button.sizeHint())
        self.like_grid_button.move(370, 20)
        self.like_grid_button.setEnabled(False)
        self.like_grid_button.clicked.connect(self.like_grid_button_clicked)
        """Grids"""
        self.placed_grids = []
        # self.current_grid_corners = []  # (top_left_x, top_left_y, bottom_right_x, bottom_right_y)
        self.current_grid = MovableGrid(scene=self.scene, color=Qt.red)  # initialize grid but don't display it

    def start_work(self):
        """Show window and allows user to draw grids"""
        self.show()

    @pyqtSlot()
    def like_grid_button_clicked(self):
        """Accept grid and append it. Initialize new grid"""
        self.current_grid.set_immutable()
        self.placed_grids.append(self.current_grid)
        # self.current_grid_corners = []
        self.current_grid = MovableGrid(scene=self.scene, color=Qt.red)

    def mousePressEvent(self, event: QMouseEvent):
        """Virtual function that handles mouse buttons click. If one is redefined, all four handlers should be."""
        if event.button() == Qt.LeftButton and len(self.current_grid.corners_coordinates) < 2:
            """If left click and grid corners are not fully specified, append mouse coordinates to grid coordinates"""
            local_mouse_coordinates = self.mapToScene(event.pos())  # convert to scene coordinates
            self.current_grid.corners_coordinates.append(local_mouse_coordinates)
            if len(self.current_grid.corners_coordinates) == 1:
                """If one corner, add grid to scene"""
                self.setWindowTitle('Left click to bottom right corner or right click to cancel')
                self.current_grid.add_grid_to_scene()
            elif len(self.current_grid.corners_coordinates) == 2:
                """If two corners, draw grid"""
                tl_x = self.current_grid.corners_coordinates[0].x()
                tl_y = self.current_grid.corners_coordinates[0].y()
                br_x = self.current_grid.corners_coordinates[1].x()
                br_y = self.current_grid.corners_coordinates[1].y()
                self.current_grid.draw_grid(tl_x, tl_y, br_x, br_y)
                self.setWindowTitle('Displaying grid. Right click to cancel grid and restart')
                self.like_grid_button.setEnabled(True)
            event.accept()  # prevent event propagation to parent widget
        elif event.button() == Qt.RightButton:
            """Right click cancels the current grid"""
            self.current_grid.clear_grid()
            self.setWindowTitle('Left click to top left grid corner')
            self.like_grid_button.setEnabled(False)
            # self.scene.addPixmap(self.rescaled_pixmap)
            event.accept()  # prevent event propagation to parent widget
        else:
            return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Virtual function called every time the mouse cursor is moved."""
        if len(self.current_grid.corners_coordinates) == 1:
            """If only a grid corner is chosen, dynamically draw grid following mouse cursor"""
            mouse_coordinates = self.mapToScene(event.pos())  # switch to scene coordinates
            tl_x = self.current_grid.corners_coordinates[0].x()
            tl_y = self.current_grid.corners_coordinates[0].y()
            self.current_grid.draw_grid(tl_x, tl_y, mouse_coordinates.x(), mouse_coordinates.y())
            event.accept()
        else:
            return super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        return super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        return super().mouseReleaseEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = GridWindow()
    view.show()
    sys.exit(app.exec_())
