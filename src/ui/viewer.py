from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QPen, QColor, QBrush, QFont, QImage
import cv2
import numpy as np

class ImageViewer(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Viewer settings
        self.setRenderHint(QPixmap.HighQualityTransform if hasattr(QPixmap, 'HighQualityTransform') else 0)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.pixmap_item = None
        self.current_image_path = None
        self._image_data = None # Store loaded cv2 image if needed
        
        self.box_items = []

    def load_image(self, file_path):
        self.current_image_path = file_path
        pixmap = QPixmap(file_path)
        
        if pixmap.isNull():
            return False

        self.scene.clear()
        self.box_items = []
        
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.setSceneRect(QRectF(pixmap.rect()))
        
        # Fit to view
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        return True

    def has_image(self):
        return self.pixmap_item is not None

    def get_image_data(self):
        # Return path or cv2 image depending on what the detector needs
        # For this example, we return the path which is simplest
        return self.current_image_path

    def draw_detections(self, detections):
        """
        Draws bounding boxes on the image.
        detections: list of dicts {'bbox': [x1, y1, x2, y2], 'label': str, 'conf': float}
        """
        # Remove old boxes
        for item in self.box_items:
            self.scene.removeItem(item)
        self.box_items.clear()
        
        pen = QPen(QColor(255, 0, 0), 3) # Red boundary
        font = QFont("Arial", 10, QFont.Bold)
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            w = x2 - x1
            h = y2 - y1
            
            # Draw Rect
            rect_item = QGraphicsRectItem(x1, y1, w, h)
            rect_item.setPen(pen)
            self.scene.addItem(rect_item)
            self.box_items.append(rect_item)
            
            # Label (Text) removed as per request
            # Only bounding box is displayed

    def wheelEvent(self, event):
        # Zoom factor
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        # Set Anchors
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Save the scene pos
        old_pos = self.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)

        # Get the new position
        new_pos = self.mapToScene(event.pos())

        # Move scene to old position
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
