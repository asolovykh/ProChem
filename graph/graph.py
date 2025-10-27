import matplotlib
matplotlib.use('Qt5Agg')
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import Gui.Resource_rc


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class VRGraph(QMainWindow):

    def __init__(self, data):
        super(VRGraph, self).__init__()
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("VaspReader (Processing Window)")
        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.figure.gca().spines['right'].set_visible(False)
        sc.figure.gca().spines['top'].set_visible(False)
        data.plot(ax=sc.axes, x=data.columns[0])

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(sc, self)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        # Create a placeholder widget to hold our toolbar and canvas.
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.show()
