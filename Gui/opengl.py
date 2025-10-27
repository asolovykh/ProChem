from PySide6.QtCore import QCoreApplication, QLocale, QSize, Qt
from PySide6.QtGui import (
    QOpenGLContext,
    QSurfaceFormat,
    QCursor,
    QFont,
    QIcon,
    QImage,
    QKeySequence,
)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMainWindow, QSizePolicy, QVBoxLayout, QWidget
import Gui.Resource_rc


class Ui_VROpenGL(object):
    def setupUi(self, VROpenGL):
        if not VROpenGL.objectName():
            VROpenGL.setObjectName("VROpenGL")
        VROpenGL.resize(400, 300)
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VROpenGL.sizePolicy().hasHeightForWidth())
        VROpenGL.setSizePolicy(sizePolicy)
        VROpenGL.setMinimumSize(QSize(400, 300))
        font = QFont()
        font.setFamilies(["Times New Roman"])
        font.setPointSize(10)
        VROpenGL.setFont(font)
        icon = QIcon()
        icon.addFile(
            r"../VR_icons/PROCHEM-logo.png",
            QSize(),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )  # u":/VRlogo/VR-logo.ico"
        VROpenGL.setWindowIcon(icon)
        # VROpenGL.setStyleSheet()
        VROpenGL.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        VROpenGL.setDockOptions(
            QMainWindow.DockOption.AllowTabbedDocks
            | QMainWindow.DockOption.AnimatedDocks
        )
        self.MainWidget = QWidget(VROpenGL)
        self.MainWidget.setObjectName("MainWidget")
        sizePolicy.setHeightForWidth(self.MainWidget.sizePolicy().hasHeightForWidth())
        self.MainWidget.setSizePolicy(sizePolicy)
        self.MainWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.verticalLayout = QVBoxLayout(self.MainWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.openGLWidget = QOpenGLWidget(self.MainWidget)
        self.openGLWidget.setObjectName("openGLWidget")

        self.verticalLayout.addWidget(self.openGLWidget)

        VROpenGL.setCentralWidget(self.MainWidget)

        self.retranslateUi(VROpenGL)

    def retranslateUi(self, VROpenGL):
        VROpenGL.setWindowTitle(
            QCoreApplication.translate("VROpenGL", "VaspReader", None)
        )

    # retranslateUi
