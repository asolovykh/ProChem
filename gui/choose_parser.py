# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRChooseParserzKIMwf.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QMainWindow,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)
import Gui.Resource_rc

class Ui_VRParserChoose(QMainWindow):

    def __init__(self):
        super(Ui_VRParserChoose, self).__init__()
        self.setupUi(self)
        self.link_elements_with_functions()
        self.show()


    def setupUi(self, VRParserChoose):
        if not VRParserChoose.objectName():
            VRParserChoose.setObjectName(u"VRParserChoose")
        VRParserChoose.resize(400, 100)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VRParserChoose.sizePolicy().hasHeightForWidth())
        VRParserChoose.setSizePolicy(sizePolicy)
        VRParserChoose.setMinimumSize(QSize(400, 100))
        VRParserChoose.setMaximumSize(QSize(400, 100))
        VRParserChoose.setFocusPolicy(Qt.NoFocus)
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRParserChoose.setWindowIcon(icon)
        VRParserChoose.setStyleSheet(u"QPushButton {\n"
"  background-color: rgb(255, 240, 202);\n"
"  color: black;\n"
"  font-weight: 600;\n"
"  border-radius: 8px;\n"
"  border: 2px solid rgb(85, 0, 127);\n"
"  border-style: outset;\n"
"  padding: 3px 3px;\n"
"  margin-top: 0px;\n"
"  outline: 0px;\n"
"}\n"
"QPushButton:disabled {\n"
"border-radius: 8px;\n"
"padding: 3px 3px;\n"
"color: black;\n"
"font-weight: 600;\n"
"border-radius: 8px;\n"
"border: 2px solid rgb(75, 75, 75);\n"
"background-color:rgb(150, 150, 150);\n"
"margin-top: 0px;\n"
"outline: 0px;\n"
"border-style: outset;\n"
"}\n"
"QPushButton:hover {\n"
"  background-color: rgb(255, 212, 137);\n"
"  border: 1px solid #000000;\n"
"  border-style: outset;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: white;\n"
"border: 3px solid #000000\n"
"}\n"
"QComboBox {\n"
"  border-radius: 8px;\n"
"  border: 2px solid #000000;\n"
"  padding: 3px 3px;\n"
"}\n"
"QComboBox:disabled {\n"
"border-radius: 8px;\n"
"padding: 3px 3px;\n"
"border-radius: 8px;\n"
"border: 2px solid rgb(75, 75, 75);\n"
""
                        "background-color:rgb(150, 150, 150);\n"
"}\n"
"QComboBox::drop-down {\n"
"  width: 18px;\n"
"  height:22px;\n"
"  padding: 0px 1px;\n"
"  border: 1px solid #000000;\n"
"  border-radius: 8px;\n"
"}\n"
"QComboBox::down-arrow {\n"
"  image: url(:/down-arrow_ico/down-arrow.ico);\n"
"  width: 18px;\n"
"  height:22px;\n"
"}\n"
"QComboBox::down-arrow:hover {\n"
"    width: 18px;\n"
"    height:22px;\n"
"    padding: 0px 1px;\n"
"    border: 1px solid #000000;\n"
"    border-radius: 8px;\n"
"	background-color: rgb(255, 229, 162);\n"
"}\n"
"QComboBox::down-arrow:pressed {\n"
"    width: 18px;\n"
"    height:22px;\n"
"    padding: 0px 1px;\n"
"    border: 0px solid #000000;\n"
"    border-radius: 8px;\n"
"	background-color: rgb(255, 232, 216);\n"
"}\n"
"QComboBox:pressed {\n"
"	background-color: rgb(255, 250, 237);\n"
"}\n"
"QFrame{\n"
"  border: 2px solid #000000;\n"
"  border-radius: 5px;\n"
"}")
        self.centralwidget = QWidget(VRParserChoose)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 16, -1, -1)
        self.ChooseMethodBox = QComboBox(self.centralwidget)
        self.ChooseMethodBox.setObjectName(u"ChooseMethodBox")

        self.verticalLayout.addWidget(self.ChooseMethodBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 12, -1, -1)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.SubmitButton = QPushButton(self.centralwidget)
        self.SubmitButton.setObjectName(u"SubmitButton")

        self.horizontalLayout.addWidget(self.SubmitButton)

        self.CancelButton = QPushButton(self.centralwidget)
        self.CancelButton.setObjectName(u"CancelButton")

        self.horizontalLayout.addWidget(self.CancelButton)

        self.horizontalLayout.setStretch(0, 2)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.setStretch(0, 5)
        self.verticalLayout.setStretch(1, 1)
        VRParserChoose.setCentralWidget(self.centralwidget)

        self.retranslateUi(VRParserChoose)

        QMetaObject.connectSlotsByName(VRParserChoose)
    # setupUi

    def link_elements_with_functions(self):
        ...

    def retranslateUi(self, VRParserChoose):
        VRParserChoose.setWindowTitle(QCoreApplication.translate("VRParserChoose", u"VaspReader", None))
        self.SubmitButton.setText(QCoreApplication.translate("VRParserChoose", u"Submit", None))
        self.CancelButton.setText(QCoreApplication.translate("VRParserChoose", u"Cancel", None))
    # retranslateUi

