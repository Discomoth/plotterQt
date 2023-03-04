
#PyQt6 imports
from PyQt6.QtWidgets import QApplication, QMainWindow

# Python imports
import sys

# Local resource imports
from windows import mainWindow

app = QApplication([])
window = mainWindow()
app.exec()