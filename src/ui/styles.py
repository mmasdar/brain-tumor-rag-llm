
# Color Palette
COLORS = {
    'header_bg': '#0f172a',    # Dark Slate styling
    'background': '#f8fafc',   # Light gray/white bg
    'primary_blue': '#2563eb', # Vibrant blue for buttons
    'text_main': '#1e293b',
    'text_light': '#ffffff',
    'danger_bg': '#fef2f2',
    'danger_text': '#991b1b',
    'border': '#e2e8f0'
}

STYLESHEET = """
QMainWindow {
    background-color: #f8fafc;
}

/* Header */
QWidget#Header {
    background-color: #0f172a;
}
QLabel#HeaderTitle {
    color: white;
    font-size: 18px;
    font-weight: bold;
}
QLabel#HeaderSubtitle {
    color: #94a3b8;
    font-size: 14px;
}

/* Toolbar */
QWidget#Toolbar {
    background-color: white;
    border-bottom: 1px solid #e2e8f0;
}
QPushButton.ToolbarBtn {
    background-color: white;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    color: #475569;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton.ToolbarBtn:hover {
    background-color: #f1f5f9;
}
QPushButton#RunBtn {
    background-color: #2563eb;
    color: white;
    border: none;
}
QPushButton#RunBtn:hover {
    background-color: #1d4ed8;
}

/* Panels */
QGroupBox {
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-top: 1em;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px;
    color: #64748b;
    font-weight: bold;
    font-size: 12px;
}

/* Right Sidebar (Report) */
QWidget#ReportPanel {
    background-color: white;
    border-left: 1px solid #e2e8f0;
}
QLabel#ReportHeader {
    color: #64748b;
    font-weight: bold;
    font-size: 12px;
    padding: 10px;
}

/* Alert Box */
QFrame#AlertBox {
    background-color: #fef2f2;
    border: 1px solid #fee2e2;
    border-radius: 6px;
}
QLabel#AlertTitle {
    color: #991b1b;
    font-weight: bold;
    font-size: 14px;
}
QLabel#AlertBody {
    color: #b91c1c;
    font-size: 11px;
}

/* Stats */
QLabel#StatLabel {
    color: #64748b;
    font-size: 11px;
    text-transform: uppercase;
}
QLabel#StatValue {
    color: #0f172a;
    font-size: 14px;
    font-weight: bold;
}
QFrame#StatCard {
    background-color: #f8fafc;
    border-radius: 6px;
    padding: 8px;
}
"""
