import torch
import cv2
import numpy as np
import os
import sys
from PyQt5.QtCore import QThread, pyqtSignal

class DetectionWorker(QThread):
    result_ready = pyqtSignal(list, object) # detections, debug_image (optional)

    def __init__(self, detector, image_path, conf_threshold):
        super().__init__()
        self.detector = detector
        self.image_path = image_path
        self.conf_threshold = conf_threshold

    def run(self):
        try:
            detections = self.detector.detect(self.image_path, self.conf_threshold)
            self.result_ready.emit(detections, None)
        except Exception as e:
            print(f"Error in detection thread: {e}")
            self.result_ready.emit([], None)

class BrainTumorDetector:
    def __init__(self):
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.load_default_model()

    def load_default_model(self):
        # Paths relative to src/
        current_dir = os.path.dirname(os.path.abspath(__file__))
        src_dir = os.path.dirname(current_dir)
        
        yolo_path = os.path.join(src_dir, 'yolov7-main')
        weights_path = os.path.join(src_dir, 'weight', 'best.pt')

        print(f"DEBUG: YOLO Path: {yolo_path}")
        print(f"DEBUG: Weights Path: {weights_path}")
        
        if not os.path.exists(yolo_path):
            print("ERROR: yolov7-main not found!")
            return
            
        if not os.path.exists(weights_path):
            print("ERROR: Weights not found!")
            return

        try:
            # Add yolov7 to path so internal imports work
            if yolo_path not in sys.path:
                sys.path.append(yolo_path)

            print("Loading YOLOv7 model...")
            self.model = torch.hub.load(yolo_path, 'custom', path_or_model=weights_path, source='local')
            self.model.to(self.device).eval()
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Failed to load model: {e}")

    def detect(self, image_path, conf_threshold=0.25):
        if self.model is None:
            print("Model not loaded.")
            return []

        # Load and resize image
        img0 = cv2.imread(image_path)
        if img0 is None:
            return []
            
        # Inference
        try:
            self.model.conf = conf_threshold
            results = self.model(img0)
            
            # Extract DataFrame format
            # columns: xmin, ymin, xmax, ymax, confidence, class, name
            df = results.pandas().xyxy[0]
            
            detections = []
            for _, row in df.iterrows():
                detections.append({
                    'label': row['name'],
                    'conf': float(row['confidence']),
                    'bbox': [int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])]
                })
            
            return detections

        except Exception as e:
            print(f"Inference Error: {e}")
            return []
