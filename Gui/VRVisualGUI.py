# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'VRVisualGUIJpJuxX.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenu, QMenuBar, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QTabWidget, QVBoxLayout,
    QWidget)
import Gui.Resource_rc

class Ui_VRVisual(object):
    def setupUi(self, VRVisual):
        if not VRVisual.objectName():
            VRVisual.setObjectName(u"VRVisual")
        VRVisual.setWindowModality(Qt.NonModal)
        VRVisual.resize(480, 212)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(VRVisual.sizePolicy().hasHeightForWidth())
        VRVisual.setSizePolicy(sizePolicy)
        VRVisual.setMinimumSize(QSize(480, 212))
        VRVisual.setMaximumSize(QSize(720, 318))
        VRVisual.setContextMenuPolicy(Qt.DefaultContextMenu)
        VRVisual.setAcceptDrops(False)
        icon = QIcon()
        icon.addFile(u":/VRlogo/VR-logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        VRVisual.setWindowIcon(icon)
        VRVisual.setAutoFillBackground(False)
        VRVisual.setStyleSheet(u"QWidget#MainWidget{\n"
"	background-image: url(:/visual/VRVisual_background.png);\n"
"	background-position: right bottom;\n"
"}\n"
"QLineEdit{\n"
"  border-radius: 8px;\n"
"  border: 2px solid rgb(109, 20, 20);\n"
"  padding: 3px 3px;\n"
"}\n"
"QLineEdit:hover{\n"
"  border-radius: 8px;\n"
"  background-color: rgb(255, 248, 231);\n"
"  border: 1px solid rgb(109, 20, 20);\n"
"  padding: 3px 3px;\n"
"}\n"
"QLineEdit:focus {\n"
"  border: 3px solid rgb(0, 0, 0);\n"
"}\n"
"\n"
"QLineEdit::placeholder {\n"
"  color: #000000;\n"
"}\n"
"QPushButton {\n"
"  background-color: rgb(255, 255, 255);\n"
"  color: black;\n"
"  font-weight: 600;\n"
"  border-radius: 8px;\n"
"  border: 2px solid rgb(109, 20, 20);\n"
"  padding: 3px 3px;\n"
"  margin-top: 0px;\n"
"  outline: 0px;\n"
"  border-style: outset;\n"
"}\n"
"QPushButton:hover {\n"
"  background-color: rgb(255, 248, 231);\n"
"  border: 1px solid rgb(74, 0, 0);\n"
"  border-style: outset;\n"
"}\n"
"QPushButton:pressed {\n"
"background-color: rgb(255, 247, 221);\n"
"borde"
                        "r: 3px solid #000000\n"
"}\n"
"QComboBox {\n"
"  border-radius: 8px;\n"
"  border: 2px solid rgb(109, 20, 20);\n"
"  padding: 3px 3px;\n"
"}\n"
"QComboBox::drop-down {\n"
"  width: 18px;\n"
"  height:22px;\n"
"  padding: 0px 1px;\n"
"  border: 1px solid rgb(109, 20, 20);\n"
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
"    border: 1px solid #000000;\n"
"    border-radius: 8px;\n"
"	background-color: rgb(255, 232, 216);\n"
"}\n"
"QComboBox:pressed {\n"
"	background-color: rgb(255, 250, 237);\n"
"	border: 3px solid #000000;\n"
"    border-radius: 8px;\n"
"}\n"
"QComboBox:hover{\n"
"  border-r"
                        "adius: 8px;\n"
"  background-color: rgb(255, 248, 231);\n"
"  border: 1px solid rgb(109, 20, 20);\n"
"  padding: 3px 3px;\n"
"}\n"
"QFrame{\n"
"  border: 2px solid rgb(109, 20, 20);\n"
"  border-radius: 5px;\n"
"	background-color: rgb(255, 255, 255);\n"
"}\n"
"QFrame:hover{\n"
"  background-color: rgb(255, 248, 231);\n"
"  border: 1px solid rgb(109, 20, 20);\n"
"  background-color: rgb(255, 248, 231);\n"
"}\n"
"QSlider{\n"
"  background-color: rgb(255, 255, 255);\n"
"}\n"
"QSlider:hover{\n"
"  background-color: rgb(255, 248, 231);\n"
"}\n"
"\n"
"QSlider::groove:horizontal{\n"
"border: 1px solid #637EB8;\n"
"background: white;\n"
"height: 7px;\n"
"border-radius: 3px;\n"
"}\n"
"QSlider::sub-page:horizontal {\n"
"background: qlineargradient(spread:reflect, x1:0.534, y1:0, x2:0.534, y2:0.5, stop:0 rgba(106, 0, 255, 255), stop:1 rgba(255, 255, 255, 255));\n"
"border: 1px solid rgb(0, 0, 0);\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"QSlider::add-page:horizontal {\n"
"background: #fff;\n"
"border: 1px solid"
                        " rgb(170, 0, 0);\n"
"height: 10px;\n"
"border-radius: 4px;\n"
"}\n"
"QSlider::handle:horizontal{\n"
"background: qlineargradient(spread:reflect, x1:0.534, y1:0, x2:0.534, y2:0.5, stop:0 rgba(106, 0, 255, 255), stop:1 rgba(255, 255, 255, 255));\n"
"border: 2px solid rgb(0, 0, 0);\n"
"width: 5px;\n"
"margin-top: -4px;\n"
"margin-bottom: -4px;\n"
"border-radius: 2px;\n"
"}")
        VRVisual.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        VRVisual.setInputMethodHints(Qt.ImhNone)
        VRVisual.setIconSize(QSize(24, 24))
        VRVisual.setToolButtonStyle(Qt.ToolButtonIconOnly)
        VRVisual.setTabShape(QTabWidget.Rounded)
        VRVisual.setDockNestingEnabled(False)
        VRVisual.setUnifiedTitleAndToolBarOnMac(False)
        self.AOpen_calculation = QAction(VRVisual)
        self.AOpen_calculation.setObjectName(u"AOpen_calculation")
        font = QFont()
        font.setFamilies([u"Times New Roman"])
        font.setPointSize(10)
        self.AOpen_calculation.setFont(font)
        self.ALoad_Calculation_State = QAction(VRVisual)
        self.ALoad_Calculation_State.setObjectName(u"ALoad_Calculation_State")
        self.ALoad_Calculation_State.setFont(font)
        self.ASave_Calculation_State = QAction(VRVisual)
        self.ASave_Calculation_State.setObjectName(u"ASave_Calculation_State")
        self.ASave_Calculation_State.setFont(font)
        self.ALoad_Configuration = QAction(VRVisual)
        self.ALoad_Configuration.setObjectName(u"ALoad_Configuration")
        self.ALoad_Configuration.setFont(font)
        self.ASave_Configuration = QAction(VRVisual)
        self.ASave_Configuration.setObjectName(u"ASave_Configuration")
        self.ASave_Configuration.setFont(font)
        self.AExit = QAction(VRVisual)
        self.AExit.setObjectName(u"AExit")
        self.AExit.setFont(font)
        self.AAxes = QAction(VRVisual)
        self.AAxes.setObjectName(u"AAxes")
        self.AAxes.setCheckable(True)
        self.AAxes.setChecked(True)
        self.ACell_boarder = QAction(VRVisual)
        self.ACell_boarder.setObjectName(u"ACell_boarder")
        self.ACell_boarder.setCheckable(True)
        self.ACell_boarder.setChecked(True)
        self.ABonds = QAction(VRVisual)
        self.ABonds.setObjectName(u"ABonds")
        self.actionChange_background = QAction(VRVisual)
        self.actionChange_background.setObjectName(u"actionChange_background")
        self.ADelete_coordinates_after_leave_cell = QAction(VRVisual)
        self.ADelete_coordinates_after_leave_cell.setObjectName(u"ADelete_coordinates_after_leave_cell")
        self.ADelete_coordinates_after_leave_cell.setCheckable(True)
        self.ADelete_coordinates_after_leave_cell.setChecked(True)
        self.ADelete_coordinates_after_leave_cell.setFont(font)
        self.ALight_1 = QAction(VRVisual)
        self.ALight_1.setObjectName(u"ALight_1")
        self.ALight_1.setFont(font)
        self.ALight_2 = QAction(VRVisual)
        self.ALight_2.setObjectName(u"ALight_2")
        self.ALight_2.setFont(font)
        self.ALight_3 = QAction(VRVisual)
        self.ALight_3.setObjectName(u"ALight_3")
        self.ALight_3.setFont(font)
        self.ALight_4 = QAction(VRVisual)
        self.ALight_4.setObjectName(u"ALight_4")
        self.ALight_4.setFont(font)
        self.ALight_5 = QAction(VRVisual)
        self.ALight_5.setObjectName(u"ALight_5")
        self.ALight_5.setFont(font)
        self.ALight_6 = QAction(VRVisual)
        self.ALight_6.setObjectName(u"ALight_6")
        self.ALight_6.setFont(font)
        self.ALight_7 = QAction(VRVisual)
        self.ALight_7.setObjectName(u"ALight_7")
        self.ALight_7.setFont(font)
        self.ALight_8 = QAction(VRVisual)
        self.ALight_8.setObjectName(u"ALight_8")
        self.ALight_8.setFont(font)
        self.AProcessing = QAction(VRVisual)
        self.AProcessing.setObjectName(u"AProcessing")
        self.AOSZICAR = QAction(VRVisual)
        self.AOSZICAR.setObjectName(u"AOSZICAR")
        self.APOSCAR = QAction(VRVisual)
        self.APOSCAR.setObjectName(u"APOSCAR")
        self.ACHGCAR = QAction(VRVisual)
        self.ACHGCAR.setObjectName(u"ACHGCAR")
        self.AIR_and_RAMAN = QAction(VRVisual)
        self.AIR_and_RAMAN.setObjectName(u"AIR_and_RAMAN")
        self.AGraphs = QAction(VRVisual)
        self.AGraphs.setObjectName(u"AGraphs")
        self.AKeyboard = QAction(VRVisual)
        self.AKeyboard.setObjectName(u"AKeyboard")
        self.AKeyboard.setCheckable(True)
        self.AMouse_keyboard = QAction(VRVisual)
        self.AMouse_keyboard.setObjectName(u"AMouse_keyboard")
        self.AMouse_keyboard.setCheckable(True)
        self.AAtom_ID = QAction(VRVisual)
        self.AAtom_ID.setObjectName(u"AAtom_ID")
        self.AAtom_ID.setCheckable(True)
        self.ABond = QAction(VRVisual)
        self.ABond.setObjectName(u"ABond")
        self.ABond.setCheckable(True)
        self.AValence_angle = QAction(VRVisual)
        self.AValence_angle.setObjectName(u"AValence_angle")
        self.AValence_angle.setCheckable(True)
        self.AScreenshot = QAction(VRVisual)
        self.AScreenshot.setObjectName(u"AScreenshot")
        self.AForm_POSCAR = QAction(VRVisual)
        self.AForm_POSCAR.setObjectName(u"AForm_POSCAR")
        self.AAbout_the_program = QAction(VRVisual)
        self.AAbout_the_program.setObjectName(u"AAbout_the_program")
        self.AAbout_window = QAction(VRVisual)
        self.AAbout_window.setObjectName(u"AAbout_window")
        self.ALatest_update = QAction(VRVisual)
        self.ALatest_update.setObjectName(u"ALatest_update")
        self.AChanges_history = QAction(VRVisual)
        self.AChanges_history.setObjectName(u"AChanges_history")
        self.ACalculation_State = QAction(VRVisual)
        self.ACalculation_State.setObjectName(u"ACalculation_State")
        self.ACalculation_State.setEnabled(False)
        self.AProgram_Configuration = QAction(VRVisual)
        self.AProgram_Configuration.setObjectName(u"AProgram_Configuration")
        self.AProgram_Configuration.setEnabled(False)
        self.ABackground = QAction(VRVisual)
        self.ABackground.setObjectName(u"ABackground")
        self.AConsole = QAction(VRVisual)
        self.AConsole.setObjectName(u"AConsole")
        self.AFileSharing = QAction(VRVisual)
        self.AFileSharing.setObjectName(u"AFileSharing")
        self.actionLight_Settings = QAction(VRVisual)
        self.actionLight_Settings.setObjectName(u"actionLight_Settings")
        self.APerspective = QAction(VRVisual)
        self.APerspective.setObjectName(u"APerspective")
        self.APerspective.setCheckable(True)
        self.APerspective.setChecked(True)
        self.AOrthographic = QAction(VRVisual)
        self.AOrthographic.setObjectName(u"AOrthographic")
        self.AOrthographic.setCheckable(True)
        self.AThreading = QAction(VRVisual)
        self.AThreading.setObjectName(u"AThreading")
        self.AThreading.setCheckable(True)
        self.AThreading.setChecked(True)
        self.AThreading.setEnabled(False)
        self.AMultiprocessing = QAction(VRVisual)
        self.AMultiprocessing.setObjectName(u"AMultiprocessing")
        self.AMultiprocessing.setCheckable(True)
        self.AMultiprocessing.setEnabled(False)
        self.LAMMPS_Processing = QAction(VRVisual)
        self.LAMMPS_Processing.setObjectName(u"LAMMPS_Processing")
        self.SRIM_Processing = QAction(VRVisual)
        self.SRIM_Processing.setObjectName(u"SRIM_Processing")
        self.VASP_Processing = QAction(VRVisual)
        self.VASP_Processing.setObjectName(u"VASP_Processing")
        self.VASP_OSZICAR = QAction(VRVisual)
        self.VASP_OSZICAR.setObjectName(u"VASP_OSZICAR")
        self.VASP_POSCAR = QAction(VRVisual)
        self.VASP_POSCAR.setObjectName(u"VASP_POSCAR")
        self.VASP_CHGCAR = QAction(VRVisual)
        self.VASP_CHGCAR.setObjectName(u"VASP_CHGCAR")
        self.VASP_IR_and_RAMAN = QAction(VRVisual)
        self.VASP_IR_and_RAMAN.setObjectName(u"VASP_IR_and_RAMAN")
        self.MainWidget = QWidget(VRVisual)
        self.MainWidget.setObjectName(u"MainWidget")
        sizePolicy.setHeightForWidth(self.MainWidget.sizePolicy().hasHeightForWidth())
        self.MainWidget.setSizePolicy(sizePolicy)
        self.MainWidget.setStyleSheet(u"")
        self.gridLayout = QGridLayout(self.MainWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(8)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setContentsMargins(-1, 12, -1, -1)
        self.CentralWidget = QWidget(self.MainWidget)
        self.CentralWidget.setObjectName(u"CentralWidget")
        self.horizontalLayout = QHBoxLayout(self.CentralWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.ToFirstStep = QPushButton(self.CentralWidget)
        self.ToFirstStep.setObjectName(u"ToFirstStep")
        font1 = QFont()
        font1.setFamilies([u"Times New Roman"])
        font1.setPointSize(12)
        font1.setBold(True)
        self.ToFirstStep.setFont(font1)

        self.horizontalLayout.addWidget(self.ToFirstStep)

        self.MoveBack = QPushButton(self.CentralWidget)
        self.MoveBack.setObjectName(u"MoveBack")
        font2 = QFont()
        font2.setFamilies([u"Times New Roman"])
        font2.setPointSize(14)
        font2.setBold(True)
        self.MoveBack.setFont(font2)

        self.horizontalLayout.addWidget(self.MoveBack)

        self.StepSliderWidget = QFrame(self.CentralWidget)
        self.StepSliderWidget.setObjectName(u"StepSliderWidget")
        sizePolicy.setHeightForWidth(self.StepSliderWidget.sizePolicy().hasHeightForWidth())
        self.StepSliderWidget.setSizePolicy(sizePolicy)
        self.StepSliderWidget.setAutoFillBackground(False)
        self.StepSliderWidget.setFrameShape(QFrame.Box)
        self.StepSliderWidget.setFrameShadow(QFrame.Sunken)
        self.StepSliderWidget.setLineWidth(3)
        self.StepSliderWidget.setMidLineWidth(1)
        self.verticalLayout_2 = QVBoxLayout(self.StepSliderWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.StepSlider = QSlider(self.StepSliderWidget)
        self.StepSlider.setObjectName(u"StepSlider")
        font3 = QFont()
        font3.setFamilies([u"Times New Roman"])
        font3.setPointSize(12)
        self.StepSlider.setFont(font3)
        self.StepSlider.setAcceptDrops(False)
        self.StepSlider.setAutoFillBackground(False)
        self.StepSlider.setSingleStep(1)
        self.StepSlider.setOrientation(Qt.Horizontal)
        self.StepSlider.setInvertedAppearance(False)
        self.StepSlider.setInvertedControls(False)
        self.StepSlider.setTickPosition(QSlider.TicksBelow)
        self.StepSlider.setTickInterval(5)

        self.verticalLayout_2.addWidget(self.StepSlider)


        self.horizontalLayout.addWidget(self.StepSliderWidget)

        self.MoveForward = QPushButton(self.CentralWidget)
        self.MoveForward.setObjectName(u"MoveForward")
        self.MoveForward.setFont(font2)

        self.horizontalLayout.addWidget(self.MoveForward)

        self.ToLastStep = QPushButton(self.CentralWidget)
        self.ToLastStep.setObjectName(u"ToLastStep")
        self.ToLastStep.setFont(font1)

        self.horizontalLayout.addWidget(self.ToLastStep)


        self.gridLayout.addWidget(self.CentralWidget, 5, 0, 1, 4)

        self.TopWidget = QHBoxLayout()
        self.TopWidget.setSpacing(6)
        self.TopWidget.setObjectName(u"TopWidget")
        self.TopWidget.setContentsMargins(-1, -1, -1, 8)
        self.DirectoryPath = QLineEdit(self.MainWidget)
        self.DirectoryPath.setObjectName(u"DirectoryPath")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Active, QPalette.PlaceholderText, brush)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Inactive, QPalette.PlaceholderText, brush)
#endif
#if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.Disabled, QPalette.PlaceholderText, brush)
#endif
        self.DirectoryPath.setPalette(palette)
        self.DirectoryPath.setFont(font)

        self.TopWidget.addWidget(self.DirectoryPath)

        self.BrowseButton = QPushButton(self.MainWidget)
        self.BrowseButton.setObjectName(u"BrowseButton")
        self.BrowseButton.setFont(font1)
        self.BrowseButton.setCursor(QCursor(Qt.PointingHandCursor))

        self.TopWidget.addWidget(self.BrowseButton)

        self.CalculationAddButton = QPushButton(self.MainWidget)
        self.CalculationAddButton.setObjectName(u"CalculationAddButton")
        self.CalculationAddButton.setFont(font1)
        self.CalculationAddButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.CalculationAddButton.setFlat(False)

        self.TopWidget.addWidget(self.CalculationAddButton)

        self.TopWidget.setStretch(0, 5)
        self.TopWidget.setStretch(1, 1)
        self.TopWidget.setStretch(2, 1)

        self.gridLayout.addLayout(self.TopWidget, 0, 0, 1, 4)

        self.LowerWidget = QWidget(self.MainWidget)
        self.LowerWidget.setObjectName(u"LowerWidget")
        self.horizontalLayout_2 = QHBoxLayout(self.LowerWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 8, 0, 8)
        self.HSpaser1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.HSpaser1)

        self.SpeedSliderWidget = QFrame(self.LowerWidget)
        self.SpeedSliderWidget.setObjectName(u"SpeedSliderWidget")
        sizePolicy.setHeightForWidth(self.SpeedSliderWidget.sizePolicy().hasHeightForWidth())
        self.SpeedSliderWidget.setSizePolicy(sizePolicy)
        self.SpeedSliderWidget.setAutoFillBackground(False)
        self.SpeedSliderWidget.setFrameShape(QFrame.Box)
        self.SpeedSliderWidget.setFrameShadow(QFrame.Sunken)
        self.SpeedSliderWidget.setLineWidth(2)
        self.SpeedSliderWidget.setMidLineWidth(1)
        self.verticalLayout = QVBoxLayout(self.SpeedSliderWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.SpeedSlider = QSlider(self.SpeedSliderWidget)
        self.SpeedSlider.setObjectName(u"SpeedSlider")
        self.SpeedSlider.setFont(font3)
        self.SpeedSlider.setAcceptDrops(False)
        self.SpeedSlider.setAutoFillBackground(False)
        self.SpeedSlider.setSingleStep(1)
        self.SpeedSlider.setOrientation(Qt.Horizontal)
        self.SpeedSlider.setInvertedAppearance(False)
        self.SpeedSlider.setInvertedControls(False)
        self.SpeedSlider.setTickPosition(QSlider.TicksBelow)
        self.SpeedSlider.setTickInterval(5)

        self.verticalLayout.addWidget(self.SpeedSlider)


        self.horizontalLayout_2.addWidget(self.SpeedSliderWidget)

        self.HSpacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.HSpacer2)

        self.horizontalLayout_2.setStretch(0, 1)
        self.horizontalLayout_2.setStretch(1, 3)
        self.horizontalLayout_2.setStretch(2, 1)

        self.gridLayout.addWidget(self.LowerWidget, 7, 0, 1, 4)

        self.StepLabalWidget = QHBoxLayout()
        self.StepLabalWidget.setObjectName(u"StepLabalWidget")
        self.HSpacer3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.StepLabalWidget.addItem(self.HSpacer3)

        self.StepLabel = QLabel(self.MainWidget)
        self.StepLabel.setObjectName(u"StepLabel")
        self.StepLabel.setAlignment(Qt.AlignCenter)

        self.StepLabalWidget.addWidget(self.StepLabel)

        self.HSpacer4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.StepLabalWidget.addItem(self.HSpacer4)

        self.StepLabalWidget.setStretch(0, 1)
        self.StepLabalWidget.setStretch(1, 5)
        self.StepLabalWidget.setStretch(2, 1)

        self.gridLayout.addLayout(self.StepLabalWidget, 6, 0, 1, 4)

        self.DeleteCalculationWidget = QHBoxLayout()
        self.DeleteCalculationWidget.setSpacing(6)
        self.DeleteCalculationWidget.setObjectName(u"DeleteCalculationWidget")
        self.DeleteCalculationWidget.setContentsMargins(-1, -1, -1, 8)
        self.AddedCalculations = QComboBox(self.MainWidget)
        self.AddedCalculations.setObjectName(u"AddedCalculations")
        self.AddedCalculations.setFont(font)
        self.AddedCalculations.setCursor(QCursor(Qt.PointingHandCursor))

        self.DeleteCalculationWidget.addWidget(self.AddedCalculations)

        self.DeleteCalculationButton = QPushButton(self.MainWidget)
        self.DeleteCalculationButton.setObjectName(u"DeleteCalculationButton")
        self.DeleteCalculationButton.setFont(font1)
        self.DeleteCalculationButton.setCursor(QCursor(Qt.PointingHandCursor))

        self.DeleteCalculationWidget.addWidget(self.DeleteCalculationButton)

        self.DeleteCalculationWidget.setStretch(0, 7)
        self.DeleteCalculationWidget.setStretch(1, 3)

        self.gridLayout.addLayout(self.DeleteCalculationWidget, 1, 0, 1, 4)

        VRVisual.setCentralWidget(self.MainWidget)
        self.VisualMenubar = QMenuBar(VRVisual)
        self.VisualMenubar.setObjectName(u"VisualMenubar")
        self.VisualMenubar.setGeometry(QRect(0, 0, 480, 21))
        self.VisualMenubar.setFont(font)
        self.VisualMenuFile = QMenu(self.VisualMenubar)
        self.VisualMenuFile.setObjectName(u"VisualMenuFile")
        self.VisualMenuFile.setFont(font)
        self.VisualMenuEdit = QMenu(self.VisualMenubar)
        self.VisualMenuEdit.setObjectName(u"VisualMenuEdit")
        self.VisualMenuEdit.setFont(font)
        self.VisualMenuLight = QMenu(self.VisualMenuEdit)
        self.VisualMenuLight.setObjectName(u"VisualMenuLight")
        self.VisualMenuLight.setFont(font)
        self.VisualMenuMods = QMenu(self.VisualMenubar)
        self.VisualMenuMods.setObjectName(u"VisualMenuMods")
        self.VisualMenuMods.setFont(font)
        self.VisualMenuSupercomputer = QMenu(self.VisualMenuMods)
        self.VisualMenuSupercomputer.setObjectName(u"VisualMenuSupercomputer")
        self.menuVASP = QMenu(self.VisualMenuMods)
        self.menuVASP.setObjectName(u"menuVASP")
        self.menuVASP.setEnabled(True)
        self.menuLAMMPS = QMenu(self.VisualMenuMods)
        self.menuLAMMPS.setObjectName(u"menuLAMMPS")
        self.menuLAMMPS.setEnabled(True)
        self.menuSRIM = QMenu(self.VisualMenuMods)
        self.menuSRIM.setObjectName(u"menuSRIM")
        self.menuSRIM.setEnabled(True)
        self.VisualMenuTools = QMenu(self.VisualMenubar)
        self.VisualMenuTools.setObjectName(u"VisualMenuTools")
        self.VisualMenuTools.setFont(font)
        self.VisualMenuSelect_mode = QMenu(self.VisualMenuTools)
        self.VisualMenuSelect_mode.setObjectName(u"VisualMenuSelect_mode")
        self.VisualMenuSelect_mode.setFont(font)
        self.VisualMenuLabel = QMenu(self.VisualMenuTools)
        self.VisualMenuLabel.setObjectName(u"VisualMenuLabel")
        self.VisualMenuLabel.setFont(font)
        self.VisualMenuHelp = QMenu(self.VisualMenubar)
        self.VisualMenuHelp.setObjectName(u"VisualMenuHelp")
        self.VisualMenuHelp.setFont(font)
        self.VisualMenuView = QMenu(self.VisualMenubar)
        self.VisualMenuView.setObjectName(u"VisualMenuView")
        self.menuProjection = QMenu(self.VisualMenuView)
        self.menuProjection.setObjectName(u"menuProjection")
        self.VisualSettings = QMenu(self.VisualMenubar)
        self.VisualSettings.setObjectName(u"VisualSettings")
        self.menuParsing_using = QMenu(self.VisualSettings)
        self.menuParsing_using.setObjectName(u"menuParsing_using")
        VRVisual.setMenuBar(self.VisualMenubar)

        self.VisualMenubar.addAction(self.VisualMenuFile.menuAction())
        self.VisualMenubar.addAction(self.VisualMenuEdit.menuAction())
        self.VisualMenubar.addAction(self.VisualMenuView.menuAction())
        self.VisualMenubar.addAction(self.VisualMenuMods.menuAction())
        self.VisualMenubar.addAction(self.VisualMenuTools.menuAction())
        self.VisualMenubar.addAction(self.VisualSettings.menuAction())
        self.VisualMenubar.addAction(self.VisualMenuHelp.menuAction())
        self.VisualMenuFile.addAction(self.AOpen_calculation)
        self.VisualMenuFile.addSeparator()
        self.VisualMenuFile.addAction(self.ACalculation_State)
        self.VisualMenuFile.addSeparator()
        self.VisualMenuFile.addAction(self.ALoad_Calculation_State)
        self.VisualMenuFile.addAction(self.ASave_Calculation_State)
        self.VisualMenuFile.addSeparator()
        self.VisualMenuFile.addAction(self.AProgram_Configuration)
        self.VisualMenuFile.addSeparator()
        self.VisualMenuFile.addAction(self.ALoad_Configuration)
        self.VisualMenuFile.addAction(self.ASave_Configuration)
        self.VisualMenuFile.addSeparator()
        self.VisualMenuFile.addAction(self.AExit)
        self.VisualMenuEdit.addAction(self.ADelete_coordinates_after_leave_cell)
        self.VisualMenuEdit.addSeparator()
        self.VisualMenuEdit.addAction(self.VisualMenuLight.menuAction())
        self.VisualMenuEdit.addSeparator()
        self.VisualMenuEdit.addAction(self.ABackground)
        self.VisualMenuLight.addAction(self.ALight_1)
        self.VisualMenuLight.addAction(self.ALight_2)
        self.VisualMenuLight.addAction(self.ALight_3)
        self.VisualMenuLight.addAction(self.ALight_4)
        self.VisualMenuLight.addAction(self.ALight_5)
        self.VisualMenuLight.addAction(self.ALight_6)
        self.VisualMenuLight.addAction(self.ALight_7)
        self.VisualMenuLight.addAction(self.ALight_8)
        self.VisualMenuLight.addSeparator()
        self.VisualMenuLight.addAction(self.actionLight_Settings)
        self.VisualMenuMods.addAction(self.menuVASP.menuAction())
        self.VisualMenuMods.addSeparator()
        self.VisualMenuMods.addAction(self.menuLAMMPS.menuAction())
        self.VisualMenuMods.addSeparator()
        self.VisualMenuMods.addAction(self.menuSRIM.menuAction())
        self.VisualMenuMods.addSeparator()
        self.VisualMenuMods.addAction(self.VisualMenuSupercomputer.menuAction())
        self.VisualMenuMods.addSeparator()
        self.VisualMenuMods.addAction(self.AGraphs)
        self.VisualMenuSupercomputer.addAction(self.AConsole)
        self.VisualMenuSupercomputer.addAction(self.AFileSharing)
        self.menuVASP.addAction(self.VASP_Processing)
        self.menuVASP.addAction(self.VASP_OSZICAR)
        self.menuVASP.addAction(self.VASP_POSCAR)
        self.menuVASP.addAction(self.VASP_CHGCAR)
        self.menuVASP.addAction(self.VASP_IR_and_RAMAN)
        self.menuLAMMPS.addAction(self.LAMMPS_Processing)
        self.menuSRIM.addAction(self.SRIM_Processing)
        self.VisualMenuTools.addAction(self.VisualMenuSelect_mode.menuAction())
        self.VisualMenuTools.addSeparator()
        self.VisualMenuTools.addAction(self.VisualMenuLabel.menuAction())
        self.VisualMenuTools.addSeparator()
        self.VisualMenuTools.addAction(self.AForm_POSCAR)
        self.VisualMenuTools.addSeparator()
        self.VisualMenuTools.addAction(self.AScreenshot)
        self.VisualMenuSelect_mode.addAction(self.AKeyboard)
        self.VisualMenuSelect_mode.addAction(self.AMouse_keyboard)
        self.VisualMenuLabel.addAction(self.AAtom_ID)
        self.VisualMenuLabel.addAction(self.ABond)
        self.VisualMenuLabel.addAction(self.AValence_angle)
        self.VisualMenuHelp.addAction(self.AAbout_the_program)
        self.VisualMenuHelp.addSeparator()
        self.VisualMenuHelp.addAction(self.AAbout_window)
        self.VisualMenuHelp.addSeparator()
        self.VisualMenuHelp.addAction(self.ALatest_update)
        self.VisualMenuHelp.addSeparator()
        self.VisualMenuHelp.addAction(self.AChanges_history)
        self.VisualMenuView.addAction(self.AAxes)
        self.VisualMenuView.addAction(self.ACell_boarder)
        self.VisualMenuView.addSeparator()
        self.VisualMenuView.addAction(self.menuProjection.menuAction())
        self.VisualMenuView.addSeparator()
        self.VisualMenuView.addAction(self.ABonds)
        self.menuProjection.addAction(self.APerspective)
        self.menuProjection.addAction(self.AOrthographic)
        self.VisualSettings.addAction(self.menuParsing_using.menuAction())
        self.menuParsing_using.addAction(self.AThreading)
        self.menuParsing_using.addAction(self.AMultiprocessing)

        self.retranslateUi(VRVisual)

        QMetaObject.connectSlotsByName(VRVisual)
    # setupUi

    def retranslateUi(self, VRVisual):
        VRVisual.setWindowTitle(QCoreApplication.translate("VRVisual", u"VaspReader", None))
        self.AOpen_calculation.setText(QCoreApplication.translate("VRVisual", u"Open calculation", None))
        self.ALoad_Calculation_State.setText(QCoreApplication.translate("VRVisual", u"Load", None))
        self.ASave_Calculation_State.setText(QCoreApplication.translate("VRVisual", u"Save", None))
        self.ALoad_Configuration.setText(QCoreApplication.translate("VRVisual", u"Load", None))
        self.ASave_Configuration.setText(QCoreApplication.translate("VRVisual", u"Save", None))
        self.AExit.setText(QCoreApplication.translate("VRVisual", u"Exit", None))
        self.AAxes.setText(QCoreApplication.translate("VRVisual", u"Axes", None))
        self.ACell_boarder.setText(QCoreApplication.translate("VRVisual", u"Cell boarder", None))
        self.ABonds.setText(QCoreApplication.translate("VRVisual", u"Bonds", None))
        self.actionChange_background.setText(QCoreApplication.translate("VRVisual", u"Change background", None))
        self.ADelete_coordinates_after_leave_cell.setText(QCoreApplication.translate("VRVisual", u"Delete coordinates after leave cell", None))
        self.ALight_1.setText(QCoreApplication.translate("VRVisual", u"Light 1", None))
        self.ALight_2.setText(QCoreApplication.translate("VRVisual", u"Light 2", None))
        self.ALight_3.setText(QCoreApplication.translate("VRVisual", u"Light 3", None))
        self.ALight_4.setText(QCoreApplication.translate("VRVisual", u"Light 4", None))
        self.ALight_5.setText(QCoreApplication.translate("VRVisual", u"Light 5", None))
        self.ALight_6.setText(QCoreApplication.translate("VRVisual", u"Light 6", None))
        self.ALight_7.setText(QCoreApplication.translate("VRVisual", u"Light 7", None))
        self.ALight_8.setText(QCoreApplication.translate("VRVisual", u"Light 8", None))
        self.AProcessing.setText(QCoreApplication.translate("VRVisual", u"Processing", None))
        self.AOSZICAR.setText(QCoreApplication.translate("VRVisual", u"OSZICAR", None))
        self.APOSCAR.setText(QCoreApplication.translate("VRVisual", u"POSCAR", None))
        self.ACHGCAR.setText(QCoreApplication.translate("VRVisual", u"CHGCAR", None))
        self.AIR_and_RAMAN.setText(QCoreApplication.translate("VRVisual", u"IR and RAMAN", None))
        self.AGraphs.setText(QCoreApplication.translate("VRVisual", u"Graphs", None))
        self.AKeyboard.setText(QCoreApplication.translate("VRVisual", u"Keyboard", None))
        self.AMouse_keyboard.setText(QCoreApplication.translate("VRVisual", u"Mouse+keyboard", None))
        self.AAtom_ID.setText(QCoreApplication.translate("VRVisual", u"Atom ID", None))
        self.ABond.setText(QCoreApplication.translate("VRVisual", u"Bond", None))
        self.AValence_angle.setText(QCoreApplication.translate("VRVisual", u"Valence angle", None))
        self.AScreenshot.setText(QCoreApplication.translate("VRVisual", u"Make a screenshot", None))
        self.AForm_POSCAR.setText(QCoreApplication.translate("VRVisual", u"Form POSCAR", None))
        self.AAbout_the_program.setText(QCoreApplication.translate("VRVisual", u"About the program", None))
        self.AAbout_window.setText(QCoreApplication.translate("VRVisual", u"About window", None))
        self.ALatest_update.setText(QCoreApplication.translate("VRVisual", u"Latest update", None))
        self.AChanges_history.setText(QCoreApplication.translate("VRVisual", u"Changes history", None))
        self.ACalculation_State.setText(QCoreApplication.translate("VRVisual", u"Calculation State", None))
        self.AProgram_Configuration.setText(QCoreApplication.translate("VRVisual", u"Program Configuration", None))
        self.ABackground.setText(QCoreApplication.translate("VRVisual", u"Background", None))
        self.AConsole.setText(QCoreApplication.translate("VRVisual", u"Console", None))
        self.AFileSharing.setText(QCoreApplication.translate("VRVisual", u"FileSharing", None))
        self.actionLight_Settings.setText(QCoreApplication.translate("VRVisual", u"Light Settings", None))
        self.APerspective.setText(QCoreApplication.translate("VRVisual", u"Perspective", None))
        self.AOrthographic.setText(QCoreApplication.translate("VRVisual", u"Orthographic", None))
        self.AThreading.setText(QCoreApplication.translate("VRVisual", u"Threading", None))
        self.AMultiprocessing.setText(QCoreApplication.translate("VRVisual", u"Multiprocessing", None))
        self.LAMMPS_Processing.setText(QCoreApplication.translate("VRVisual", u"Processing", None))
        self.SRIM_Processing.setText(QCoreApplication.translate("VRVisual", u"Processing", None))
        self.VASP_Processing.setText(QCoreApplication.translate("VRVisual", u"Processing", None))
        self.VASP_OSZICAR.setText(QCoreApplication.translate("VRVisual", u"OSZICAR", None))
        self.VASP_POSCAR.setText(QCoreApplication.translate("VRVisual", u"POSCAR", None))
        self.VASP_CHGCAR.setText(QCoreApplication.translate("VRVisual", u"CHGCAR", None))
        self.VASP_IR_and_RAMAN.setText(QCoreApplication.translate("VRVisual", u"IR and RAMAN", None))
        self.ToFirstStep.setText(QCoreApplication.translate("VRVisual", u"<<", None))
        self.MoveBack.setText(QCoreApplication.translate("VRVisual", u"<", None))
#if QT_CONFIG(tooltip)
        self.StepSlider.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.MoveForward.setText(QCoreApplication.translate("VRVisual", u">", None))
        self.ToLastStep.setText(QCoreApplication.translate("VRVisual", u">>", None))
        self.DirectoryPath.setText("")
        self.DirectoryPath.setPlaceholderText(QCoreApplication.translate("VRVisual", u"Input calculation folder", None))
        self.BrowseButton.setText(QCoreApplication.translate("VRVisual", u"Browse", None))
        self.CalculationAddButton.setText(QCoreApplication.translate("VRVisual", u"Add", None))
#if QT_CONFIG(tooltip)
        self.SpeedSlider.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.StepLabel.setText("")
        self.AddedCalculations.setCurrentText("")
        self.AddedCalculations.setPlaceholderText(QCoreApplication.translate("VRVisual", u"Choose calculation to delete", None))
        self.DeleteCalculationButton.setText(QCoreApplication.translate("VRVisual", u"Delete", None))
        self.VisualMenuFile.setTitle(QCoreApplication.translate("VRVisual", u"File", None))
        self.VisualMenuEdit.setTitle(QCoreApplication.translate("VRVisual", u"Edit", None))
        self.VisualMenuLight.setTitle(QCoreApplication.translate("VRVisual", u"Light", None))
        self.VisualMenuMods.setTitle(QCoreApplication.translate("VRVisual", u"Mods", None))
        self.VisualMenuSupercomputer.setTitle(QCoreApplication.translate("VRVisual", u"Supercomputer", None))
        self.menuVASP.setTitle(QCoreApplication.translate("VRVisual", u"VASP", None))
        self.menuLAMMPS.setTitle(QCoreApplication.translate("VRVisual", u"LAMMPS", None))
        self.menuSRIM.setTitle(QCoreApplication.translate("VRVisual", u"SRIM", None))
        self.VisualMenuTools.setTitle(QCoreApplication.translate("VRVisual", u"Tools", None))
        self.VisualMenuSelect_mode.setTitle(QCoreApplication.translate("VRVisual", u"Selection type", None))
        self.VisualMenuLabel.setTitle(QCoreApplication.translate("VRVisual", u"Label", None))
        self.VisualMenuHelp.setTitle(QCoreApplication.translate("VRVisual", u"Help", None))
        self.VisualMenuView.setTitle(QCoreApplication.translate("VRVisual", u"View", None))
        self.menuProjection.setTitle(QCoreApplication.translate("VRVisual", u"Projection", None))
        self.VisualSettings.setTitle(QCoreApplication.translate("VRVisual", u"Settings", None))
        self.menuParsing_using.setTitle(QCoreApplication.translate("VRVisual", u"Parsing using", None))
    # retranslateUi

