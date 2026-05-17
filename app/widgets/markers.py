import numpy as np
import cv2
from cv2.aruco import getPredefinedDictionary, DICT_4X4_50
from PySide6.QtWidgets import QWidget, QLabel, QSizePolicy
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt

class MarkersWidget(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.marker_size = 150
        self.aruco_dict = getPredefinedDictionary(DICT_4X4_50)
        self.point = -1

    def createCanva(self):
        self.canvas = np.zeros((self.height(), self.width(), 4), dtype=np.uint8) * 255
        
        if self.height() < self.marker_size:
            return
        if self.width() < self.marker_size:
            return

        positions = [
            (0, 0),
            (0, self.width() - self.marker_size),
            (self.height() - self.marker_size, self.width() - self.marker_size),
            (self.height() - self.marker_size, 0)
        ]
        
        for marker_id, (row, col) in enumerate(positions):
            marker = cv2.aruco.generateImageMarker(self.aruco_dict, marker_id, self.marker_size - 30)
            
            padding = cv2.copyMakeBorder(marker, 15, 15, 15, 15, cv2.BORDER_CONSTANT, value=255)
            background_with_padding = cv2.cvtColor(padding, cv2.COLOR_GRAY2BGR)
 
            if marker_id == self.point:
                cv2.circle(background_with_padding, (self.marker_size//2, self.marker_size//2), 10, (255, 0, 0), -1)           

            self.canvas[row:row+self.marker_size, col:col+self.marker_size, :3] = background_with_padding
            self.canvas[row:row+self.marker_size, col:col+self.marker_size, 3] = 255

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateImage()

    def updateImage(self):
        self.createCanva()

        bytesPerLine = 4 * self.width()
        image = QImage(
            self.canvas.data,
            self.width(),
            self.height(),
            bytesPerLine,
            QImage.Format.Format_RGBA8888
        )

        pixmap = QPixmap(image)

        self.setPixmap(pixmap)

    def setPoint(self, i):
        self.point = i
        self.updateImage()