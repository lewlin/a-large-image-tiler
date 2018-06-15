import sys
import numpy as np
from PyQt5.QtCore import Qt, QSize, QRect, QPointF, pyqtSlot, QRectF, QPoint
from PyQt5.QtGui import QMouseEvent, QPixmap, QIcon, QTransform, QPolygonF, \
    QPainterPath, QPainter, QImage, QBrush
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene


class BackgroundImage:
    """"
    Handle an bg_image/bg_image files: show bg_image in scene, rotate,
    cropped a region, etc.
    """
    def __init__(self):
        self.img_file = None
        self.image = None  # QImage
        self.scaling_factor = None  # from displayed to original
        self.img_width = None  # of original image
        self.img_height = None  # of original image

        self.rotation = QTransform()  # rotate image to flat out grid angle
        self.rotated_image = None
        self.angle = None  # CCW (rad)

        self.translation = QTransform()  # translate ref so that (0,0) is tl

    def show_in_scene(self, view):
        """
            Rescale QPixmap to scene and show it in view.

        Parameters
        ----------
        view:
            QGraphicsScene

        Returns
        -------

        """
        pixmap = QPixmap.fromImage(self.image)
        pixmap_scaled = pixmap.scaledToHeight(view.height())
        view.scene.addPixmap(pixmap_scaled)
        orig_size = pixmap.size()
        scaled_size = pixmap_scaled.size()
        self.scaling_factor = scaled_size.height() / orig_size.height()

    def image_from_file(self, file_name):
        """
        Load a TIFF bg_image from file `file_name`
        as a QImage and set it to `self.image`.

        Parameters
        ----------
        file_name: str
            full path of bg_image file

        Returns
        -------

        """
        self.image = QImage(file_name)
        self.img_width = self.image.width()
        self.img_height = self.image.height()

    def rotate_image(self, angle):
        """
            Rotate image CW by `angle` (in rad).
            Set `self.rotated_image`.
        :param angle:
        :return:
        """

        """Rotate image to flat grid angle"""
        self.angle = angle
        self.rotation.rotateRadians(angle)  # rotate CW (CCW if angle < 0)
        self.rotated_image = self.image.transformed(self.rotation)

        """DEBUG: show rotated image w/o translation"""
        # paint = QPainter(self.rotated_image)
        # paint.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        # paint.drawRect(0, 0, 100, 100)
        # paint.end()
        # self.rotated_image.save('rotated.tiff')
        # print('rotated image by', self.angle)

        """Set translated frame so that top-left corner of image is (0, 0)"""
        phi = -self.angle  # phi in grid geometry notation
        print('PHI:', phi)
        if 0 < phi < np.pi/2:
            dy = np.sin(phi) * self.img_width
            dx = 0
        elif np.pi/2 <= phi < np.pi:
            eps = phi - np.pi/2
            dx = self.img_width * np.sin(eps)
            dy = self.img_width * np.cos(eps) + self.img_height * np.sin(eps)
        else:
            raise NotImplementedError
        print('Translating by', dx, dy)
        self.translation.translate(dx, dy)

        """DEBUG: draw transformed rect to image top-left corner"""
        paint2 = QPainter(self.rotated_image)
        paint2.setBrush(QBrush(Qt.green, Qt.SolidPattern))
        new_tl = self.map_2_rotated_frame(QPoint(0, 0))
        print(new_tl)
        paint2.drawRect(new_tl.x()-50, new_tl.y()-50, 100, 100)
        paint2.end()
        self.rotated_image.save('transf.tiff')

    def map_2_rotated_frame(self, item):
        """
        Map item to rotated reference.
        :param item
            item in un-rotated coordinates

        :return:
            item in rotated coordinates
        """
        if self.rotation is not None:
            rotated_item = self.rotation.map(item)
        else:
            rotated_item = item

        if self.translation is not None:
            return self.translation.map(rotated_item)
        else:
            return None

    def del_rotated_image(self):
        del self.rotated_image

    def crop_region(self, coords, angle, file_name):
        """

        :param coords:
        :param angle:
        :param file_name:
        :return:
        """

        tl, bl, br, tr = coords
        print('Original coords', tl, br)

        """Scale polygon coordinates to original image size"""
        scaled_coords = []
        for coord in coords:
            scaled_coords.append(coord / self.scaling_factor)
        tl, bl, br, tr = scaled_coords
        print('Scaled coords', tl, br)

        """Cast polygon coordinates to rotated image reference"""
        if self.rotation is not None:
            rotated_coords = []
            for scaled_coord in scaled_coords:
                rotated_coords.append(self.map_2_rotated_frame(scaled_coord))
            tl, bl, br, tr = rotated_coords
        else:
            tl, bl, br, tr = scaled_coords

        print('Rotated coords', tl, br)

        # corner = self.map_2_rotated_frame(QPointF(0, 0))
        # print('new corner', corner)

        """Find rectangle to be cropped"""
        scaled_rect = QRectF(tl, br).toRect()
        # w = self.rotated_image.width()
        # h = self.rotated_image.height()
        # scaled_rect = QRectF(QPointF(0, 0), QPointF(w, h)).toRect()
        height = scaled_rect.height()
        width = scaled_rect.width()
        scaled_rect_size = QSize(width, height)

        try:
            """Create small image to paste grid square into"""
            cropped_image = self.rotated_image.copy(scaled_rect)

            """Use a `QPainter` to draw on `destination_image`"""
            bg_format = self.image.format()
            destination_image = QImage(scaled_rect_size, bg_format)
            destination_image.fill(Qt.transparent)  # fill it w transparent bg
            painter = QPainter(destination_image)
            painter.drawImage(
                QRect(0, 0, width, height),
                cropped_image
            )
            painter.end()  # generate an error if I don't call it

        except TypeError as err:
            print('No bg_image loaded?', err)
        except AttributeError as err:
            print('Could not copy pixmap?', err)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        else:
            destination_image.save(file_name + '.tif')
