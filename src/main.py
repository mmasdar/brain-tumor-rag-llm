import sys
import os

# Add the src directory to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt5.QtWidgets import QApplication
from ui.window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set app style/palette here if needed for generic "dark mode" or similar
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
