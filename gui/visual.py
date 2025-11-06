from PySide6.QtCore import QCoreApplication, QLocale, QSize, Qt
from PySide6.QtGui import (QOpenGLContext, QSurfaceFormat,
    QCursor, QFont, QIcon, QImage)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from gui.opengl_widget import GLWidget
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QWidget
import gui.resource_rc


class Ui_Visual(object):

    def setupUi(self, Visual, settings, project_directory):
        if not Visual.objectName():
            Visual.setObjectName("Visual")
        Visual.resize(400, 300)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Visual.sizePolicy().hasHeightForWidth())
        Visual.setSizePolicy(sizePolicy)
        Visual.setMinimumSize(QSize(400, 300))
        font = QFont()
        font.setFamilies(["Times New Roman"])
        font.setPointSize(10)
        Visual.setFont(font)
        Visual.setWindowIcon(QIcon(":/icons/logo/PROCHEM-logo.ico"))
        Visual.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        Visual.setDockOptions(
            QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.AnimatedDocks
        )
        self.MainWidget = QWidget(Visual)
        self.MainWidget.setObjectName("MainWidget")
        sizePolicy.setHeightForWidth(self.MainWidget.sizePolicy().hasHeightForWidth())
        self.MainWidget.setSizePolicy(sizePolicy)
        self.MainWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.verticalLayout = QVBoxLayout(self.MainWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.openGLWidget = GLWidget(self.MainWidget, settings, project_directory)
        self.openGLWidget.setObjectName("openGLWidget")

        self.verticalLayout.addWidget(self.openGLWidget)

        Visual.setCentralWidget(self.MainWidget)

        self.retranslateUi(Visual)

    def retranslateUi(self, Visual):
        Visual.setWindowTitle(QCoreApplication.translate("Visual", "PROCHEM", None))
