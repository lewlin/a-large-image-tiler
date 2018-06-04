import sys
from PyQt5.QtCore import Qt, QSize, QRect, QPointF, pyqtSlot, QRectF
from PyQt5.QtGui import QMouseEvent, QPixmap, QIcon, QTransform, QPolygonF, \
    QPainterPath, QPainter, QImage
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

        self.rotation = None
        self.rotated_image = None
        self.angle = None

    def show_in_scene(self, view):
        """
            Rescale QPixmap to scene and show it.

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

    def rotate_image(self, angle):
        print('rotate_image is called')
        self.rotation = QTransform()
        self.rotation.rotateRadians(angle)
        self.angle = angle
        self.rotated_image = self.image.transformed(self.rotation)

    def map_item(self, item):
        """
        Map item to rotated reference.
        :param item
            item in un-rotated coordinates

        :return:
            item in rotated coordinates
        """

        if self.rotation is not None:
            return self.rotation.map(item)
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

        print('angle', angle)

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
                rotated_coords.append(self.map_item(scaled_coord))
            tl, bl, br, tr = rotated_coords
        else:
            tl, bl, br, tr = scaled_coords

        print('Rotated coords', tl, br)

        corner = self.map_item(QPointF(0, 0))
        print('new corner', corner)

        """Find rectangle to be cropped"""
        scaled_rect = QRectF(tl, br).toRect()
        # TODO rotation do not account for translating coordinate system.
        # TODO FIX THAT!
        # TODO there are large images in history. Images should never be outputted
        # TODO to git directory. Also, I need to remove that from history.
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
