from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QProgressBar, QSizePolicy, 
                             QFileDialog, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSlot, QSize, QDate, QBuffer, QIODevice, QByteArray
from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap, QPainter, QTextDocument, QPen
from PyQt5.QtPrintSupport import QPrinter

from .viewer import ImageViewer
from .styles import STYLESHEET
from backend.detector import BrainTumorDetector, DetectionWorker
import numpy as np

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Brain Metastases Diagnosis System")
        self.resize(1280, 800)
        self.setStyleSheet(STYLESHEET)

        # Backend
        self.detector = BrainTumorDetector()
        
        # State
        self.current_detections = []
        self.diagnosis_results = {
            'prob': 0,
            'lesion_count': 0,
            'diagnosis': "Unknown"
        }

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 1. Header
        self.create_header()

        # 2. Toolbar
        self.create_toolbar()

        # 3. Content Area (Split Left/Right)
        content_wrapper = QWidget()
        content_layout = QHBoxLayout(content_wrapper)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Left: Viewport
        self.create_viewport(content_layout)
        
        # Right: Report Panel
        self.create_report_panel(content_layout)
        
        self.main_layout.addWidget(content_wrapper)

    def create_header(self):
        header = QWidget()
        header.setObjectName("Header")
        header.setFixedHeight(60)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        # Title
        title = QLabel("BRAIN METASTASES DIAGNOSYS SYSTEM")
        title.setObjectName("HeaderTitle")
        
        # Right side branding
        branding = QLabel("Brawijaya University")
        branding.setObjectName("HeaderSubtitle")

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(branding)
        
        self.main_layout.addWidget(header)

    def create_toolbar(self):
        toolbar = QWidget()
        toolbar.setObjectName("Toolbar")
        toolbar.setFixedHeight(70)
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)

        # Buttons
        self.btn_import = QPushButton("  Import MRI")
        self.btn_import.setIcon(self.style().standardIcon(self.style().SP_DirOpenIcon))
        self.btn_import.setProperty("class", "ToolbarBtn")
        self.btn_import.setCursor(Qt.PointingHandCursor)
        self.btn_import.clicked.connect(self.load_image)

        self.btn_sample = QPushButton("  Load Sample")
        self.btn_sample.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.btn_sample.setProperty("class", "ToolbarBtn")
        self.btn_sample.setCursor(Qt.PointingHandCursor)

        self.btn_run = QPushButton("  Run Diagnosis")
        self.btn_run.setObjectName("RunBtn")
        self.btn_run.setIcon(self.style().standardIcon(self.style().SP_MediaPlay))
        self.btn_run.setProperty("class", "ToolbarBtn") 
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.clicked.connect(self.run_detection)
        self.btn_run.setEnabled(False) 
        self.btn_run.setFixedWidth(180)

        layout.addWidget(self.btn_import)
        layout.addWidget(self.btn_sample)
        layout.addStretch()
        layout.addWidget(self.btn_run)

        self.main_layout.addWidget(toolbar)

    def create_viewport(self, parent_layout):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Label above image
        header_lbl = QLabel("MRI VIEWPORT [AXIAL T1]")
        header_lbl.setStyleSheet("color: #64748b; font-weight: bold; font-size: 12px; padding-bottom: 8px;")
        layout.addWidget(header_lbl)

        # Frame for Viewer
        viewer_frame = QFrame()
        viewer_frame.setStyleSheet("background-color: black; border-radius: 8px;")
        vf_layout = QVBoxLayout(viewer_frame)
        vf_layout.setContentsMargins(1, 1, 1, 1) # Thin border

        self.viewer = ImageViewer()
        self.viewer.setStyleSheet("background-color: black; border: none;")
        vf_layout.addWidget(self.viewer)
        
        layout.addWidget(viewer_frame)
        
        # Add shadow to container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        container.setGraphicsEffect(shadow)

        parent_layout.addWidget(container, stretch=2)

    def create_report_panel(self, parent_layout):
        self.report_panel = QWidget()
        self.report_panel.setObjectName("ReportPanel")
        self.report_panel.setStyleSheet("background-color: white; border-radius: 8px;")
        
        layout = QVBoxLayout(self.report_panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Panel Header
        lbl_title = QLabel("DIAGNOSTIC REPORT")
        lbl_title.setObjectName("ReportHeader")
        layout.addWidget(lbl_title)

        # 1. Alert Box (Hidden by default, shown on result)
        self.alert_box = QFrame()
        self.alert_box.setObjectName("AlertBox")
        alert_layout = QHBoxLayout(self.alert_box)
        
        # Icon placeholder (text for now)
        icon_lbl = QLabel("!")
        icon_lbl.setStyleSheet("background-color: #fee2e2; color: #991b1b; border-radius: 12px; padding: 4px 10px; font-weight: bold;")
        
        text_layout = QVBoxLayout()
        self.lbl_alert_title = QLabel("Abnormality Detected")
        self.lbl_alert_title.setObjectName("AlertTitle")
        self.lbl_alert_msg = QLabel("High-confidence lesion identified.")
        self.lbl_alert_msg.setObjectName("AlertBody")
        self.lbl_alert_msg.setWordWrap(True)
        text_layout.addWidget(self.lbl_alert_title)
        text_layout.addWidget(self.lbl_alert_msg)

        alert_layout.addWidget(icon_lbl)
        alert_layout.addLayout(text_layout)
        
        self.alert_box.hide() # Initially hidden
        layout.addWidget(self.alert_box)

        # 2. Model & Prob
        prob_container = QWidget()
        p_layout = QVBoxLayout(prob_container)
        p_layout.setContentsMargins(0,0,0,0)
        
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Prediction Model"))
        row1.addStretch()
        row1.addWidget(QLabel("ResNet-50 / YOLOv8")) 
        
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Malignancy Probability"))
        row2.addStretch()
        self.lbl_prob = QLabel("0.0%")
        self.lbl_prob.setStyleSheet("font-weight: bold; color: #2563eb;")
        row2.addWidget(self.lbl_prob)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #2563eb; border-radius: 3px; } QProgressBar { background-color: #e2e8f0; border-radius: 3px; border: none; }")
        self.progress_bar.setValue(0)

        p_layout.addLayout(row1)
        p_layout.addSpacing(5)
        p_layout.addLayout(row2)
        p_layout.addWidget(self.progress_bar)
        
        layout.addWidget(prob_container)

        # 3. Stats Grid
        grid_container = QWidget()
        g_layout = QHBoxLayout(grid_container)
        g_layout.setSpacing(10)
        g_layout.setContentsMargins(0,0,0,0)

        # Lesion Count Card
        card_count = QFrame()
        card_count.setObjectName("StatCard")
        cs_layout = QVBoxLayout(card_count)
        cs_layout.addWidget(QLabel("LESION COUNT", objectName="StatLabel"))
        self.lbl_count = QLabel("-", objectName="StatValue")
        cs_layout.addWidget(self.lbl_count)
        g_layout.addWidget(card_count)

        # Diagnosis Card
        card_diag = QFrame()
        card_diag.setObjectName("StatCard")
        ct_layout = QVBoxLayout(card_diag)
        ct_layout.addWidget(QLabel("DIAGNOSIS", objectName="StatLabel"))
        self.lbl_diagnosis = QLabel("-", objectName="StatValue")
        ct_layout.addWidget(self.lbl_diagnosis)
        g_layout.addWidget(card_diag)

        layout.addWidget(grid_container)

        # 4. Findings
        layout.addWidget(QLabel("CLINICAL FINDINGS", styleSheet="font-weight:bold; color:#64748b; font-size:12px; margin-top:10px;"))
        self.list_findings = QListWidget()
        self.list_findings.setStyleSheet("border: none; background: transparent; font-size: 13px;")
        self.list_findings.addItem("• Load an image to start diagnosis.")
        layout.addWidget(self.list_findings, stretch=1)

        # 5. Export Button
        self.btn_export = QPushButton("Export PDF Report")
        self.btn_export.setStyleSheet("""
            QPushButton { background-color: #1e293b; color: white; border-radius: 6px; padding: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #334155; }
        """)
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.clicked.connect(self.export_report)
        layout.addWidget(self.btn_export)

        # Shadow for panel
        shadow_panel = QGraphicsDropShadowEffect()
        shadow_panel.setBlurRadius(20)
        shadow_panel.setColor(QColor(0,0,0,20))
        shadow_panel.setOffset(0, 0)
        self.report_panel.setGraphicsEffect(shadow_panel)

        parent_layout.addWidget(self.report_panel, stretch=1)

    @pyqtSlot()
    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MRI Image", "", 
                                                   "Images (*.png *.jpg *.jpeg *.bmp *.tif);;All Files (*)", 
                                                   options=options)
        if file_path:
            self.viewer.load_image(file_path)
            self.btn_run.setEnabled(True)
            self.btn_run.setStyleSheet("background-color: #2563eb;") 
            self.reset_report()

    def reset_report(self):
        self.alert_box.hide()
        self.lbl_prob.setText("0.0%")
        self.progress_bar.setValue(0)
        self.lbl_count.setText("-")
        self.lbl_diagnosis.setText("-")
        self.list_findings.clear()
        self.list_findings.addItem("• Ready to analyze.")
        self.diagnosis_results = {'prob': 0, 'lesion_count': 0, 'diagnosis': "Unknown"}
        self.current_detections = []

    @pyqtSlot()
    def run_detection(self):
        if not self.viewer.has_image():
            return

        self.btn_run.setEnabled(False)
        self.btn_run.setText("Analyzing...")
        self.reset_report() 
        
        # Use Thread
        image_path = self.viewer.get_image_data()
        self.worker = DetectionWorker(self.detector, image_path, 0.25)
        self.worker.result_ready.connect(self.on_detection_complete)
        self.worker.start()

    def on_detection_complete(self, detections, _):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("  Run Diagnosis")
        
        self.current_detections = detections
        self.viewer.draw_detections(detections)
        self.update_report(detections)


    def update_report(self, detections):
        if not detections:
            self.alert_box.hide()
            self.list_findings.clear()
            self.list_findings.addItem("• No Abnormalities Detected.")
            self.diagnosis_results = {'prob': 0, 'lesion_count': 0, 'diagnosis': "Normal"}
            return

        # Show Alert
        self.alert_box.show()
        
        # Get highest confidence
        best_det = max(detections, key=lambda x: x['conf'])
        prob_val = int(best_det['conf'] * 100)
        
        self.lbl_prob.setText(f"{prob_val}.0%")
        self.progress_bar.setValue(prob_val)
        self.diagnosis_results['prob'] = prob_val
        
        # IMPLEMENTATION OF NEW LOGIC
        lesion_count = len(detections)
        self.lbl_count.setText(str(lesion_count))
        self.diagnosis_results['lesion_count'] = lesion_count
        
        if lesion_count == 1:
            diagnosis_text = "Not Metastases"
        elif lesion_count > 1:
            diagnosis_text = "Metastases"
        else:
            diagnosis_text = "Unknown"
        
        self.lbl_diagnosis.setText(diagnosis_text)
        self.diagnosis_results['diagnosis'] = diagnosis_text

        # Clinical findings
        self.list_findings.clear()
        self.list_findings.addItem(f"• Detected {lesion_count} lesion(s).")
        self.list_findings.addItem(f"• Diagnosis: {diagnosis_text}")
        self.list_findings.addItem(f"• Max Confidence: {prob_val}%")
        self.list_findings.addItem(f"• Primary lesion: {best_det['label']}")


    @pyqtSlot()
    def export_report(self):
        if not self.viewer.has_image():
            QMessageBox.warning(self, "Export Error", "No image loaded to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(self, "Export PDF Report", "Detection_Report.pdf", "PDF Files (*.pdf)")
        if not filename:
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(filename)
        printer.setPageSize(QPrinter.A4)

        # 1. Grab Image
        image_path = self.viewer.current_image_path
        if image_path:
            image_pixmap = QPixmap(image_path)
            
            # Draw detections if any
            if self.current_detections:
                painter = QPainter(image_pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                pen = QPen(QColor(255, 0, 0), 5) 
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                
                for det in self.current_detections:
                    x1, y1, x2, y2 = det['bbox']
                    w = x2 - x1
                    h = y2 - y1
                    painter.drawRect(int(x1), int(y1), int(w), int(h))
                
                painter.end()
        else:
            image_pixmap = QPixmap(400, 300)
            image_pixmap.fill(Qt.black)

        # Save pixmap to buffer to embed in HTML
        ba = QByteArray()
        buffer = QBuffer(ba)
        buffer.open(QIODevice.WriteOnly)
        image_pixmap.save(buffer, "PNG")
        import base64
        image_data = base64.b64encode(ba.data()).decode("utf-8")
        
        # 2. Build HTML Content
        current_date = QDate.currentDate().toString(Qt.DefaultLocaleLongDate)
        
        # Findings to HTML
        findings_html = "<ul>"
        for i in range(self.list_findings.count()):
            item = self.list_findings.item(i)
            findings_html += f"<li>{item.text()}</li>"
        findings_html += "</ul>"

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; padding: 40px; color: #333; }}
                h1 {{ color: #1e293b; font-size: 24px; border-bottom: 2px solid #334155; padding_bottom: 10px; }}
                .header {{ display: flex; justify-content: space-between; margin-bottom: 30px; }}
                .meta {{ color: #64748b; font-size: 12px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 25px; }}
                .label {{ font-weight: bold; color: #475569; }}
                .value {{ color: #0f172a; }}
                .image-container {{ text-align: center; margin: 20px 0; border: 1px solid #ddd; padding: 10px; }}
                img {{ max-width: 100%; height: auto; }}
                .stats-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                .stats-table td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Brain Metastases Diagnostic Report</h1>
            </div>
            
            <div class="meta">
                Date: {current_date}<br>
                Generated by: GUI Brain Metastases System
            </div>

            <div class="section">
                <h3>Diagnosis Results</h3>
                <table class="stats-table">
                    <tr>
                        <td class="label">Malignancy Probability</td>
                        <td class="value">{self.diagnosis_results.get('prob', 0)}%</td>
                    </tr>
                    <tr>
                        <td class="label">Lesion Count</td>
                        <td class="value">{self.diagnosis_results.get('lesion_count', 0)}</td>
                    </tr>
                    <tr>
                        <td class="label">Diagnosis</td>
                        <td class="value">{self.diagnosis_results.get('diagnosis', 'N/A')}</td>
                    </tr>
                </table>
            </div>

            <div class="section image-container">
                <h3>Visual Analysis</h3>
                <img src="data:image/png;base64,{image_data}" width="500">
            </div>

            <div class="section">
                <h3>Clinical Findings</h3>
                {findings_html}
            </div>
        </body>
        </html>
        """

        # 3. Print
        document = QTextDocument()
        document.setHtml(html_content)
        document.print_(printer)
        
        QMessageBox.information(self, "Success", f"Report successfully exported to {filename}")
