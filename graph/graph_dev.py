import time

import numpy as np
import pandas as pd
from Gui.VRGraphProcessingGUI import Ui_VRGraphProcessing, QMainWindow
from PySide6.QtWidgets import QGraphicsScene, QApplication, QGraphicsTextItem, QGraphicsItem, QGraphicsLineItem, QGraphicsItemGroup
from PySide6.QtGui import QPen, QColor, QBrush
from PySide6.QtCore import Qt


class VRScene(QGraphicsScene):

    def __init__(self, sceneSize=(0, 0, 800, 600), backgroundColor=(1.0, 1.0, 1.0, 1.0)):
        super(VRScene, self).__init__()
        self._sceneSize = sceneSize
        self._backgroundColor = QColor().fromRgbF(*backgroundColor)
        self.setSceneRect(*self._sceneSize)
        self.setBackgroundBrush(self._backgroundColor)


class VRGraphObjectsGroup(QGraphicsItemGroup):

    def __init__(self, *args):
        super(VRGraphObjectsGroup, self).__init__(*args)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsLineItem.GraphicsItemFlag.ItemContainsChildrenInShape, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

    def mousePressEvent(self, event):
        if self.isSelected():
            self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)

    def focusOutEvent(self, event):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)

    def itemChange(self, change, value):
        if QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return QGraphicsTextItem.itemChange(self, change, value)
        elif QGraphicsItem.GraphicsItemChange.ItemScaleChange:
            return QGraphicsTextItem.itemChange(self, change, value)


class VRGraphEditableText(QGraphicsTextItem):

    def __init__(self, text, position, orientation=0):
        super(VRGraphEditableText, self).__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        #self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self._orientation = orientation
        self.setPos(*position)
        self.setHtml(text)
        self.setRotation(orientation)

    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        if self._orientation:
            self.setRotation(0)

        #self.setHtml(f'<item style=\"; background-color:#ffffff;\">{self.document().toRawText()}</item>')
        #self.focusItem()

    def focusOutEvent(self, event):
        self.setPlainText(self.document().toPlainText())
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        if self._orientation:
            self.setRotation(self._orientation)
        #self.setHtml(self.document().toRawText())

    def itemChange(self, change, value):
        if QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return QGraphicsTextItem.itemChange(self, change, value)
        elif QGraphicsItem.GraphicsItemChange.ItemScaleChange:
            return QGraphicsTextItem.itemChange(self, change, value)


class VRGraphText(QGraphicsTextItem):

    def __init__(self, text, position=(0, 0), orientation=0):
        super(VRGraphText, self).__init__()
        self._orientation = orientation
        self.setPos(*position)
        self.setPlainText(text)
        self.setRotation(orientation)


class VRGraphLine(QGraphicsLineItem):

    def __init__(self, x1, y1, x2, y2, lineWidth=3, color=(0.0, 0.0, 0.0, 1.0), position=(0.0, 0.0), isMovable=False, isSelectable=False):
        super(VRGraphLine, self).__init__(x1, y1, x2, y2)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, isMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, isSelectable)
        colorLine = QColor()
        colorLine.setRgbF(*color)
        self.setPen(QPen(colorLine, lineWidth))
        self.position = position
        if self.position:
            self.setPos(*position)

    def itemChange(self, change, value):
        if QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            return QGraphicsTextItem.itemChange(self, change, value)
        elif QGraphicsItem.GraphicsItemChange.ItemScaleChange:
            return QGraphicsTextItem.itemChange(self, change, value)


class VRXaxis(VRGraphObjectsGroup):

    def __init__(self, position=(50, 550), axisLength=700, axisWidth=3, isOuterTicks=True, ticksNumber=5, ticksLength=6, subticksEnable=False, subticksNumber=1):
        super(VRXaxis, self).__init__()

        self.position, self.axisLength, self._axisWidth = position, axisLength, axisWidth
        self._isOuterTicks, self.ticksNumber, self._ticksLength = isOuterTicks, ticksNumber, ticksLength
        self._subticksEnable, self._subticksNumber = subticksEnable, subticksNumber

        self._axisLine = VRGraphLine(position[0], position[-1], position[0] + axisLength, position[-1], axisWidth)
        self.addToGroup(self._axisLine)

        if isOuterTicks:
            self.axisTicksCoordinates = [(position[0] + axisLength / ticksNumber * i, position[-1],
                                           position[0] + axisLength / ticksNumber * i, position[-1] + ticksLength)
                                          for i in range(0, ticksNumber + 1)]
        else:
            self.axisTicksCoordinates = [(position[0] + axisLength / ticksNumber * i, position[-1],
                                           position[0] + axisLength / ticksNumber * i, position[-1] - ticksLength)
                                          for i in range(0, ticksNumber + 1)]
        self._axisTicks = [VRGraphLine(*self.axisTicksCoordinates[i], lineWidth=axisWidth)
                           for i in range(1, ticksNumber + 1)]

        self._subticks = None
        if subticksEnable:
            if isOuterTicks:
                subticksInterval = axisLength / (ticksNumber * (subticksNumber + 1))
                self.subticksCoordinates = [(position[0] + axisLength / ticksNumber * i + subticksInterval * j,
                                              position[-1],
                                              position[0] + axisLength / ticksNumber * i + subticksInterval * j,
                                              position[-1] + ticksLength // 2)
                                             for i in range(0, ticksNumber) for j in range(1, subticksNumber + 1)]
            else:
                subticksInterval = axisLength / (ticksNumber * (subticksNumber + 1))
                self.subticksCoordinates = [(position[0] + axisLength / ticksNumber * i + subticksInterval * j,
                                              position[-1],
                                              position[0] + axisLength / ticksNumber * i + subticksInterval * j,
                                              position[-1] - ticksLength // 2)
                                             for i in range(0, ticksNumber) for j in range(1, subticksNumber + 1)]
            self._subticks = [VRGraphLine(*self.subticksCoordinates[i], lineWidth=axisWidth)
                              for i in range(0, len(self.subticksCoordinates))]

        if self._subticks is not None:
            [self.addToGroup(self._subticks[i]) for i in range(len(self._subticks))]
        [self.addToGroup(self._axisTicks[i]) for i in range(len(self._axisTicks))]

    def mouseDoubleClickEvent(self, event):
        if self.group():
            print(self.group())


class VRYaxis(VRGraphObjectsGroup):

    def __init__(self, position=(50, 550), axisLength=500, axisWidth=3, isOuterTicks=True, ticksNumber=5, ticksLength=6, subticksEnable=False, subticksNumber=1):
        super(VRYaxis, self).__init__()

        self.position, self.axisLength, self._axisWidth = position, axisLength, axisWidth
        self._isOuterTicks, self.ticksNumber, self._ticksLength = isOuterTicks, ticksNumber, ticksLength
        self._subticksEnable, self._subticksNumber = subticksEnable, subticksNumber

        self._axisLine = VRGraphLine(position[0], position[-1], position[0], position[-1] - axisLength, axisWidth)
        self.addToGroup(self._axisLine)

        if isOuterTicks:
            self.axisTicksCoordinates = [(position[0], position[-1] - axisLength / ticksNumber * i,
                                          position[0] - ticksLength, position[-1] - axisLength / ticksNumber * i)
                                         for i in range(0, ticksNumber + 1)]
        else:
            self.axisTicksCoordinates = [(position[0], position[-1] - axisLength / ticksNumber * i,
                                           position[0] + ticksLength, position[-1] - axisLength / ticksNumber * i)
                                         for i in range(0, ticksNumber + 1)]
        self._axisTicks = [VRGraphLine(*self.axisTicksCoordinates[i], lineWidth=axisWidth)
                           for i in range(1, ticksNumber + 1)]

        self._subticks = None
        if subticksEnable:
            if isOuterTicks:
                subticksInterval = axisLength / (ticksNumber * (subticksNumber + 1))
                self.subticksCoordinates = [(position[0],
                                             position[-1] - axisLength / ticksNumber * i - subticksInterval * j,
                                             position[0] - ticksLength // 2,
                                             position[-1] - axisLength / ticksNumber * i - subticksInterval * j)
                                            for i in range(0, ticksNumber) for j in range(1, subticksNumber + 1)]
            else:
                subticksInterval = axisLength / (ticksNumber * (subticksNumber + 1))
                self.subticksCoordinates = [(position[0],
                                              position[-1] - axisLength / ticksNumber * i - subticksInterval * j,
                                              position[0] + ticksLength // 2,
                                              position[-1] - axisLength / ticksNumber * i - subticksInterval * j)
                                            for i in range(0, ticksNumber) for j in range(1, subticksNumber + 1)]
            self._subticks = [VRGraphLine(*self.subticksCoordinates[i], lineWidth=axisWidth)
                              for i in range(0, len(self.subticksCoordinates))]

        if self._subticks is not None:
            [self.addToGroup(self._subticks[i]) for i in range(len(self._subticks))]
        [self.addToGroup(self._axisTicks[i]) for i in range(len(self._axisTicks))]

    def mouseDoubleClickEvent(self, event):
        if self.group():
            print(self.group())


class VRGrid(VRGraphObjectsGroup):

    def __init__(self, XaxisObject, YaxisObject, isGridEnable=True, gridWidth=1, isGridLine=True, gridLinesNumber=10, gridColor=(0.0, 0.0, 0.0, 1.0), isSubgridEnable=False, subgridWidth=1, isSubridLine=True, subgridColor='black'):
        super(VRGrid, self).__init__()

        self._Xaxis = XaxisObject
        self._Yaxis = YaxisObject

        self._Xgrid = None
        if isGridEnable:
            if isGridLine:
                self._Xgrid = [VRGraphLine(*self._Xaxis.axisTicksCoordinates[i][:-1],
                                           self._Xaxis.axisTicksCoordinates[i][1] - self._Yaxis.axisLength,
                                           lineWidth=gridWidth, color=gridColor)
                               for i in range(len(self._Xaxis.axisTicksCoordinates))]
            else:
                linesGrid = np.linspace(self._Xaxis.position[1], self._Xaxis.position[1] - self._Yaxis.axisLength, gridLinesNumber + 1)
                distance = (linesGrid[1] - linesGrid[0]) /2
                self._Xgrid = [VRGraphLine(self._Xaxis.axisTicksCoordinates[i][0],
                                           linesGrid[num + 1],
                                           self._Xaxis.axisTicksCoordinates[i][2],
                                           linesGrid[num + 1] - distance,
                                           lineWidth=gridWidth, color=gridColor)
                               for i in range(1, len(self._Xaxis.axisTicksCoordinates))
                               for num, length in enumerate(linesGrid[:-1])]
            [self.addToGroup(self._Xgrid[i]) for i in range(len(self._Xgrid))]

        self._Ygrid = None
        if isGridEnable:
            if isGridLine:
                self._Ygrid = [VRGraphLine(*self._Yaxis.axisTicksCoordinates[i][:2],
                                           self._Yaxis.axisTicksCoordinates[i] + self._Xaxis.axisLength,
                                           self._Yaxis.axisTicksCoordinates[i][-1],
                                           lineWidth=gridWidth, color=gridColor)
                               for i in range(len(self._Yaxis.axisTicksCoordinates))]
            else:
                linesGrid = np.linspace(self._Yaxis.position[0], self._Yaxis.position[0] + self._Xaxis.axisLength, gridLinesNumber + 1)
                distance = (linesGrid[1] - linesGrid[0]) /2
                self._Ygrid = [VRGraphLine(linesGrid[num + 1],
                                           self._Yaxis.axisTicksCoordinates[i][1],
                                           linesGrid[num + 1] - distance,
                                           self._Yaxis.axisTicksCoordinates[i][-1],
                                           lineWidth=gridWidth, color=gridColor)
                               for i in range(1, len(self._Yaxis.axisTicksCoordinates))
                               for num, length in enumerate(linesGrid[:-1])]
            [self.addToGroup(self._Ygrid[i]) for i in range(len(self._Ygrid))]


class VRXaxisTickNumbers(VRGraphObjectsGroup):

    def __init__(self, XaxisObject, xMin=0, xMax=1, stringFormat='.2f'):
        super(VRXaxisTickNumbers, self).__init__()
        self._Xaxis = XaxisObject
        self._xMin, self._xMax = xMin, xMax
        self._ticks = np.linspace(self._xMin, self._xMax, self._Xaxis.ticksNumber + 1).tolist()
        self._formatStr = '{0:' + stringFormat + '}'
        self._ticksStr = map(lambda x: self._formatStr.format(x), self._ticks)
        self._ticksText = [VRGraphText(tickStr) for num, tickStr in enumerate(self._ticksStr)]
        for num, tick in enumerate(self._ticksText):
            boundingRectSize = tick.boundingRect().getCoords()
            xCenter = (boundingRectSize[2] -boundingRectSize[0]) / 2
            yCenter = (boundingRectSize[3] -boundingRectSize[1]) / 2
            tick.setPos(self._Xaxis.axisTicksCoordinates[num][0] - xCenter, self._Xaxis.axisTicksCoordinates[num][1])
        [self.addToGroup(self._ticksText[i]) for i in range(len(self._ticksText))]


class VRYaxisTickNumbers(VRGraphObjectsGroup):

    def __init__(self, YaxisObject, yMin=0, yMax=1, stringFormat='.2f'):
        super(VRYaxisTickNumbers, self).__init__()
        self._Yaxis = YaxisObject
        self._yMin, self._yMax = yMin, yMax
        self._ticks = np.linspace(self._yMin, self._yMax, self._Yaxis.ticksNumber + 1).tolist()
        self._formatStr = '{0:' + stringFormat + '}'
        self._ticksStr = map(lambda x: self._formatStr.format(x), self._ticks)
        self._ticksText = [VRGraphText(tickStr) for num, tickStr in enumerate(self._ticksStr)]
        for num, tick in enumerate(self._ticksText):
            boundingRectSize = tick.boundingRect().getCoords()
            xCenter = (boundingRectSize[2] -boundingRectSize[0]) / 2
            yCenter = (boundingRectSize[3] -boundingRectSize[1]) / 2
            tick.setPos(self._Yaxis.axisTicksCoordinates[num][0] - boundingRectSize[2], self._Yaxis.axisTicksCoordinates[num][1] - yCenter)
        [self.addToGroup(self._ticksText[i]) for i in range(len(self._ticksText))]


class VRLinearGraph(VRGraphObjectsGroup):

    def __init__(self, xValues, yValues, xAxisObject, yAxisObject, lineWidth=2, lineColor=(0.0, 0.0, 0.0, 1.0)):
        super(VRLinearGraph, self).__init__()
        self._xValues, self._yValues = np.array(xValues), np.array(yValues)
        self._xAxisObject, self._yAxisObject = xAxisObject, yAxisObject
        self.lineWidth, self.colorLine = lineWidth, lineColor

        self._xMin, self._xMax = self._xValues.min(), self._xValues.max()
        self._yMin, self._yMax = self._yValues.min(), self._yValues.max()

        self._xValuesRescaled = (self._xValues - self._xMin) * (self._xAxisObject.axisLength / (self._xMax - self._xMin))
        self._yValuesRescaled = (self._yValues - self._yMin) * (self._yAxisObject.axisLength / (self._yMax - self._yMin))

        self._lines = [VRGraphLine(self._xValuesRescaled[i], -self._yValuesRescaled[i], self._xValuesRescaled[i + 1],
                                   -self._yValuesRescaled[i + 1], lineWidth=self.lineWidth, color=self.colorLine)
                       for i, _ in enumerate(self._xValuesRescaled[:-1])]
        [self.addToGroup(line) for line in self._lines]
        self.setPos(*self._xAxisObject.position)


class VRScatterGraph(VRGraphObjectsGroup):

    def __init__(self, xValues, yValues, xAxisObject, yAxisObject, pointsWidth=2, pointsColor=(0.0, 0.0, 0.0, 1.0)):
        super(VRScatterGraph, self).__init__()
        self._xValues, self._yValues = np.array(xValues), np.array(yValues)
        self._xAxisObject, self._yAxisObject = xAxisObject, yAxisObject
        self.lineWidth, self.colorLine = pointsWidth, pointsColor

        self._xMin, self._xMax = self._xValues.min(), self._xValues.max()
        self._yMin, self._yMax = self._yValues.min(), self._yValues.max()

        self._xValuesRescaled = (self._xValues - self._xMin) * (self._xAxisObject.axisLength / (self._xMax - self._xMin))
        self._yValuesRescaled = (self._yValues - self._yMin) * (self._yAxisObject.axisLength / (self._yMax - self._yMin))

        self._lines = [VRGraphLine(self._xValuesRescaled[i], -self._yValuesRescaled[i], self._xValuesRescaled[i],
                                   -self._yValuesRescaled[i], lineWidth=self.lineWidth, color=self.colorLine)
                       for i, _ in enumerate(self._xValuesRescaled)]
        [self.addToGroup(line) for line in self._lines]
        self.setPos(*self._xAxisObject.position)


class VRGraphsProcessing(Ui_VRGraphProcessing, QMainWindow):
    __defaultXaxisPosition = [400, 570]
    __defaultYaxisPosition = [0, 300]

    def __init__(self, dataframe, app=None, settings=None):
        super(VRGraphsProcessing, self).__init__()
        self.__app = app
        self.__settings = settings
        self.__dataframe = dataframe

        self._xMin, self._xMax = 0, 1
        self._yMin, self._yMax = 0, 1

        self.setupUi(self)

        self._Axes = VRGraphObjectsGroup()

        self._Xaxis = VRXaxis(axisWidth=1, subticksEnable=True, subticksNumber=1, isOuterTicks=True)
        self._Yaxis = VRYaxis(axisWidth=1, subticksEnable=True, subticksNumber=4, isOuterTicks=True)

        self._Axes.addToGroup(self._Xaxis)
        self._Axes.addToGroup(self._Yaxis)

        self._Xticks = VRXaxisTickNumbers(self._Xaxis)
        self._Yticks = VRYaxisTickNumbers(self._Yaxis)

        self._Axes.addToGroup(self._Xticks)
        self._Axes.addToGroup(self._Yticks)

        self._grid = VRGrid(self._Xaxis, self._Yaxis, isGridLine=False, gridLinesNumber=50, gridColor=(0.9, 0.9, 0.9, 1.0))
        self._Axes.addToGroup(self._grid)

        self.__scene = VRScene()
        self.__scene.setSceneRect(0, 0, 800, 600)

        self._YaxisText = VRGraphEditableText('Y-axis Name', orientation=-90, position=self.__defaultYaxisPosition)
        self._YtextBoundingRect = self._YaxisText.boundingRect().getCoords()
        self._YaxisTextXCenter = (self._YtextBoundingRect[2] - self._YtextBoundingRect[0]) / 2
        self._YaxisTextYCenter = (self._YtextBoundingRect[3] - self._YtextBoundingRect[1]) / 2
        self._YaxisText.setPos(self.__defaultYaxisPosition[0], self.__defaultYaxisPosition[1] + self._YaxisTextXCenter)
        self.__scene.addItem(self._YaxisText)

        self._XaxisText = VRGraphEditableText('X-axis Name', orientation=0, position=self.__defaultXaxisPosition)
        self._XtextBoundingRect = self._XaxisText.boundingRect().getCoords()
        self._XaxisTextXCenter = (self._XtextBoundingRect[2] - self._XtextBoundingRect[0]) / 2
        self._XaxisTextYCenter = (self._XtextBoundingRect[3] - self._XtextBoundingRect[1]) / 2
        self._XaxisText.setPos(self.__defaultXaxisPosition[0] - self._XaxisTextXCenter, self.__defaultXaxisPosition[1])
        self.__scene.addItem(self._XaxisText)

        tStart = time.time()
        self._graph = VRLinearGraph(dataframe['Time, fs'], dataframe['E_Si20'], self._Xaxis, self._Yaxis, lineWidth=2, lineColor=(1.0, 0.0, 1.0, 1.0)) # 'E_C31'
        self._Axes.addToGroup(self._graph)
        tEnd = time.time()
        print(tEnd - tStart)
        self.__scene.addItem(self._Axes)

        self.GraphsView.setScene(self.__scene)


        # self.include_label = False
        # self.event, self.value = None, None
        # self.x_lim = [0, max(self.dataframe[self.dataframe.columns[0]])]
        # self.y_lim = [None, None]
        # self.legend = dict()
        # self.label = ['', '']
        # self.is_x_limit, self.is_y_limit, self.is_legend, self.is_label = False, False, False, False
        # self.width_line, self.color_line = dict(), dict()
        # self.fig = matplotlib.figure.Figure(figsize=(5, 4), dpi=110)
        # self.fig_canvas_agg = self.draw_figure()

    def getDF(self):
        return self.__dataframe

    # def draw_figure(self):
    #     """Function of drawing figures in canvas element."""
    #     figure_canvas_agg = FigureCanvasTkAgg(self.fig, self.window['-CANVAS-'].TKCanvas)
    #     figure_canvas_agg.draw()
    #     figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    #     return figure_canvas_agg
    #
    # def delete_figure_agg(self):
    #     """Function of clearing canvas element."""
    #     self.fig_canvas_agg.get_tk_widget().forget()
    #     plt.close('all')
    #
    # def get_graph(self):
    #     """Function of drawing plot using matplotlib. Function suggesting user such options as: X and Y setting of
    #     plot limits, including legend to plot, setting of line width and curve color."""
    #     if self.fig_canvas_agg:
    #         self.delete_figure_agg()
    #     figure = matplotlib.figure.Figure(figsize=(5, 4), dpi=110)
    #     if self.is_x_limit and self.is_y_limit:
    #         self.fig_canvas_agg = figure.add_subplot(111, xlim=self.x_lim, ylim=self.y_lim)
    #     elif self.is_x_limit and not self.is_y_limit:
    #         self.fig_canvas_agg = figure.add_subplot(111, xlim=self.x_lim)
    #     elif not self.is_x_limit and self.is_y_limit:
    #         self.fig_canvas_agg = figure.add_subplot(111, ylim=self.y_lim)
    #     elif not self.is_x_limit and not self.is_y_limit:
    #         self.fig_canvas_agg = figure.add_subplot(111)
    #     for column in self.value['GraphList']:
    #         self.fig_canvas_agg.plot(self.dataframe[self.dataframe.columns[0]], self.dataframe[column], linewidth=self.width_line[column], color=self.color_line[column])
    #     if self.is_legend:
    #         legend = [self.legend[column] for column in self.value['GraphList']]
    #         figure.legend(legend, loc='upper right')
    #     axes = figure.gca()
    #     axes.spines['top'].set_visible(False)
    #     axes.spines['right'].set_visible(False)
    #     if self.is_label:
    #         axes.set_xlabel(self.label[0], fontsize=12, color='black')
    #         axes.set_ylabel(self.label[1], fontsize=12, color='black')
    #     return figure
    #
    # def column_select_elements_reaction(self, disabled):
    #     self.window['fromX'].update(disabled=disabled)
    #     self.window['toX'].update(disabled=disabled)
    #     self.window['fromY'].update(disabled=disabled)
    #     self.window['toY'].update(disabled=disabled)
    #     self.window['Xlim'].update(disabled=disabled)
    #     self.window['Ylim'].update(disabled=disabled)
    #     self.window['Reset'].update(disabled=disabled)
    #     self.window['RenameLegend'].update(disabled=disabled)
    #     self.window['CurveChoose'].update(disabled=disabled)
    #     self.window['ColorApply'].update(disabled=disabled)
    #     self.window['X-axisName'].update(disabled=disabled)
    #     self.window['Y-axisName'].update(disabled=disabled)
    #
    # def auto_rename_legend(self):
    #     legend_name = self.value['RenameLegend']
    #     if 'E' in legend_name:
    #         legend = []
    #         if 'COM' in legend_name or 'Sum' in legend_name:
    #             atoms_number = Counter(sorted(legend_name.split('_')[2:][::2]))
    #             atoms = list()
    #             for atom in atoms_number:
    #                 if atoms_number[atom] != 1:
    #                     atoms.append(f'${atom}_{str(atoms_number[atom])}$' if atoms_number[atom] < 10 else f'{atom}{str(atoms_number[atom])}')
    #                 else:
    #                     atoms.append(atom)
    #             combination_atoms = itertools.permutations(atoms)
    #             for combination in combination_atoms:
    #                 if 'COM' in legend_name:
    #                     legend.append('Translational energy of ' + ''.join(combination))
    #                     legend.append('Поступательная энергия ' + ''.join(combination))
    #                 else:
    #                     legend.append('Summary energy of ' + ''.join(combination))
    #                     legend.append('Суммарная кинетическая энергия ' + ''.join(combination))
    #         else:
    #             legend = ['Kinetic energy of ' + legend_name.split('_')[1],
    #                            'Кинетическая энергия атома ' + legend_name.split('_')[1]]
    #         self.window['AutoRename'].update(values=legend)
    #
    # def mainloop(self):
    #     self.window['GraphList'].update(values=self.dataframe.columns[1:])
    #     refresh = False
    #     while True:
    #         self.event, self.value = self.window.read(timeout=10)
    #         if self.event == 'OutCalc' or self.event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
    #             # if self.fig_canvas_agg:
    #             #     self.delete_figure_agg()
    #             self.window.close()
    #             self.print('Graph window closed.')
    #             break
    #         if refresh:
    #             self.fig = self.get_graph()
    #             self.fig_canvas_agg = self.draw_figure()
    #             refresh = False
    #         if self.event == 'GraphList':
    #             if self.value['GraphList']:
    #                 self.column_select_elements_reaction(False)
    #                 if self.window['RenameLegend']:
    #                     self.window['LegendName'].update(disabled=False)
    #                     self.window['LApply'].update(disabled=False)
    #             else:
    #                 self.column_select_elements_reaction(True)
    #                 self.window['LegendName'].update(disabled=True)
    #                 self.window['LApply'].update(disabled=True)
    #                 self.window['LineWidth'].update(disabled=True)
    #                 self.window['ChCurCol'].update(disabled=True)
    #                 self.window['CurCol'].update(disabled=True)
    #             self.x_lim = [None, max(self.dataframe[self.dataframe.columns[0]])]
    #             self.y_lim = [None, None]
    #             self.is_x_limit, self.is_y_limit, self.is_legend, self.is_label = False, False, True, False
    #             self.width_line = {column: None for column in self.value['GraphList']}
    #             self.color_line = {column: None for column in self.value['GraphList']}
    #             self.legend = {column: column for column in self.value['GraphList']}
    #             self.window['CurveChoose'].update(values=list(self.legend.keys()))
    #             self.window['RenameLegend'].update(values=list(self.legend.keys()))
    #             self.window['LineWidth'].update(disabled=True)
    #             self.window['ChCurCol'].update(disabled=True)
    #             self.window['CurCol'].update(disabled=True)
    #             self.window['ColorApply'].update(disabled=True)
    #             self.graph_name = '__'.join(self.value['GraphList'])
    #             refresh = True
    #         if self.event == 'RenameLegend':
    #             self.window['LegendName'].update(disabled=False)
    #             self.window['LegendName'].update(self.legend[self.value['RenameLegend']])
    #             self.window['AutoRename'].update(disabled=False)
    #             self.window['LApply'].update(disabled=False)
    #             self.auto_rename_legend()
    #         if self.event == 'AutoRename':
    #             self.window['LegendName'].update(disabled=False)
    #             self.window['LegendName'].update(self.value['AutoRename'])
    #             self.window['LApply'].update(disabled=False)
    #         if self.event == 'LApply':
    #             for column in self.legend:
    #                 if column == self.value['RenameLegend']:
    #                     self.legend[column] = self.value['LegendName']
    #             self.window['RenameLegend'].update('')
    #             self.window['RenameLegend'].update(values=list(self.legend.keys()))
    #             self.window['LegendName'].update('')
    #             self.window['LegendName'].update(disabled=True)
    #             self.window['LApply'].update(disabled=True)
    #             self.window['AutoRename'].update(disabled=True)
    #             self.window['AutoRename'].update(values=[])
    #             self.print(f'The name of the legend has been changed. The legend now includes:\n {str(self.value["RenameLegend"])}.')
    #             refresh = True
    #         if self.event == 'CurveChoose':
    #             self.window['LineWidth'].update(disabled=False)
    #             self.window['ChCurCol'].update(disabled=False)
    #             self.window['CurCol'].update(disabled=False)
    #             self.window['ColorApply'].update(disabled=False)
    #         if self.event == 'LineWidth' and self.value['LineWidth']:
    #             try:
    #                 in_as_float = float(self.value['LineWidth'].replace(',', '.'))
    #             except:
    #                 if not (len(self.value['LineWidth']) == 1 and self.value['LineWidth'][0] == '-'):
    #                     self.window['LineWidth'].update(self.value['LineWidth'][:-1])
    #         if self.event == 'CurCol':
    #             if self.value['CurCol'] != 'None':
    #                 self.window['cur_col'].Update(button_color=self.value['CurCol'])
    #         if self.event == 'ColorApply':
    #             color = self.value['CurCol']
    #             if color == '' or color == 'n':
    #                 color = None
    #             self.color_line[self.value['CurveChoose']] = color
    #             if self.value['LineWidth']:
    #                 try:
    #                     width = self.value['LineWidth']
    #                     width = float(width.replace(',', '.'))
    #                 except ValueError:
    #                     self.popup('Width value must be number!', title='EmptyFolderNameError')
    #                 else:
    #                     self.width_line[self.value['CurveChoose']] = width
    #             refresh = True
    #         if self.event == 'GraphCreate':
    #             if self.value['GraphList']:
    #                 graphdir = sg.PopupGetFile(message='Input directory to save graph', default_path=self.graph_name, title='Save graph', save_as=True, no_window=True, keep_on_top=True, file_types=(("PNG File", "*.png"), ("JPG File", "*.jpg *.jpeg"), ("EPS File", "*.eps"), ("PDF File", "*.pdf"), ("SVG File", "*.svg"), ("TIFF File", "*.tiff *.tif")))
    #                 if graphdir:
    #                     self.fig.savefig(graphdir, bbox_inches='tight', dpi=300)
    #                     self.print(f'Graph {graphdir.split("/")[-1]} has been created.')
    #         if self.event == 'Xlim':
    #             if self.value['fromX']:
    #                 self.x_lim[0] = float(self.value['fromX'].replace(',', '.'))
    #             else:
    #                 self.x_lim[0] = None
    #             if self.value['toX']:
    #                 self.x_lim[1] = float(self.value['toX'].replace(',', '.'))
    #             else:
    #                 self.x_lim[1] = None
    #             self.print(f'X-range changed ----> [{str(self.x_lim)}]')
    #             self.is_x_limit = True
    #             refresh = True
    #         if self.event == 'Ylim':
    #             if self.value['fromY']:
    #                 self.y_lim[0] = float(self.value['fromY'].replace(',', '.'))
    #             else:
    #                 self.y_lim[0] = None
    #             if self.value['toY']:
    #                 self.y_lim[1] = float(self.value['toY'].replace(',', '.'))
    #             else:
    #                 self.y_lim[1] = None
    #             self.print(f'Y-range changed ----> [{str(self.y_lim)}]')
    #             self.is_y_limit = True
    #             refresh = True
    #         if self.event == 'Reset':
    #             self.x_lim = [None, None]
    #             self.y_lim = [None, None]
    #             self.is_x_limit, self.is_y_limit = False, False
    #             self.window['fromX'].update('')
    #             self.window['toX'].update('')
    #             self.window['fromY'].update('')
    #             self.window['toY'].update('')
    #             self.print('X-range and Y-range reseted.')
    #             refresh = True
    #         if self.event == 'LegendIncl':
    #             self.is_legend = True if self.value['LegendIncl'] else False
    #             refresh = True
    #         if self.event == 'LALS':
    #             self.label[0] = self.value['X-axisName']
    #             self.label[1] = self.value['Y-axisName']
    #             self.is_label = True if self.label[0] or self.label[1] else False
    #             refresh = True


app = QApplication()
df = pd.read_excel(r'C:\Users\AlexS\Documents\Программирование\VaspReaderStable\TEST_CALCULATION\TestExcel.xlsx')
print(df)
window = VRGraphsProcessing(df)
window.show()
app.exec()
