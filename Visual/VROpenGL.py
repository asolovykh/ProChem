import OpenGL
from numba import jit
from numba.core.types import int64
import numpy as np
import os
from os import environ
from Visual.VRPrimitives import Primitives
import random
import time
from PIL import Image
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.WGL import *
import pygame
from pygame.locals import *
from Visual.VRVBO import VRVBO
from Visual.Shaders.VRShaders import VRShaders
from Logs.VRLogger import sendDataToLogger


def TransformVec3(vecA, mat44) -> tuple[list[float], int]:
    """Transform 3d vector to 2d projection."""
    vecB = [0, 0, 0, 0]
    for i0 in range(0, 4):
        vecB[i0] = vecA[0] * mat44[0 * 4 + i0] + vecA[1] * mat44[1 * 4 + i0] + vecA[2] * mat44[2 * 4 + i0] + mat44[3 * 4 + i0]
    return [vecB[0] / vecB[3], vecB[1] / vecB[3], vecB[2] / vecB[3]], vecB[3]


def perspectiveChoose(prjMat, mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with perspective view.
       prjMat - projection matrix, mpos - mouse position at the screen,
       ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    llNdc = [[0.0 for i in range(3)] for m in range(len(ll))]
    inRectCounter = 0  # atoms in sphere counter
    depth = list()  # atoms in sphere list
    mult = [0.0 for _ in range(len(ll))]  # коэффициенты масштабирования пространства
    for num in range(len(ll)):
        llNdc[num], mult[num] = TransformVec3(ll[num], prjMat)  # координаты в мировом пространстве???
    radii = [parameter[i] / mult[i] * 1.0 for i in range(len(ll))]  # radius of projected sphere
    ndc = [2.0 * mpos[0] / dis[0] - 1.0, 1.0 - 2.0 * mpos[1] / dis[1]]
    inRect = [0 for _ in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if llNdc[num][0] - radii[num] <= ndc[0] <= llNdc[num][0] + radii[num] and llNdc[num][1] - radii[num] <= ndc[1] <= llNdc[num][1] + radii[num]:
            inRect[num] = 1
        else:
            inRect[num] = 0
    for num in range(len(ll)):
        if inRect[num] == 1:
            inRectCounter += 1  # число попаданий
            depth.append(llNdc[num][2])  # координаты по глубине
    if inRectCounter > 1:
        rightVec = min(depth)
        for num in range(len(ll)):
            if llNdc[num][2] != rightVec:
                inRect[num] = 0
    return inRect


def orthographicChoose(mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with orthographic view.
    mpos - mouse position at the screen, ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    orthoSize = (12, 9)
    coordinate = [(1.0 - 2.0 * mpos[0] / dis[0]) * orthoSize[0], (1.0 - 2.0 * mpos[1] / dis[1]) * orthoSize[1]]
    inRectCounter = 0  # atoms in sphere counter
    depth = []  # atoms in sphere list
    inRect = [0 for m in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if ll[num][0] - parameter[num] <= coordinate[0] <= ll[num][0] + parameter[num] and ll[num][2] - parameter[num] <= coordinate[1] <= ll[num][2] + parameter[num]:
            inRect[num] = 1
        else:
            inRect[num] = 0
    for num in range(len(ll)):
        if inRect[num] == 1:
            inRectCounter += 1  # число попаданий
            depth.append(ll[num][1])  # координаты по глубине
    if inRectCounter > 1:
        rightVec = max(depth)
        for num in range(len(ll)):
            if ll[num][1] != rightVec:
                inRect[num] = 0
    return inRect


def buildProjectionMatrix(screeWidth, screeHeight, eyePoint, fov, near, far):
    """Build the projection matrix according to the formula:
    f / aspect     , 0.0             , 0.0                            , 0.0
    0.0            , f               , 0.0                            , 0.0
    0.0            , 0.0             , (far + near) / (near - far)    , -1.0
    0.0            , 0.0             , 2.0 * far * near / (near - far), 0.0
    where f = 1 / tg(fov / 2.0), aspect = screeWidth / screeHeight."""
    aspect = screeWidth / float(screeHeight)
    fov = np.radians(fov)
    f = 1 / np.tan(fov / 2.0)
    pMatrix = np.array([[f / aspect, 0.0, 0.0, 0.0],
                        [0.0, f, 0.0, 0.0],
                        [0.0, 0.0, -(far + (abs(eyePoint) + near)) / (far - (abs(eyePoint) + near)), -1.0],
                        [0.0, 0.0, -2.0 * far * (abs(eyePoint) + near) / (far - (abs(eyePoint) + near)), 0.0]], np.float32)
    return pMatrix


def buildOrthographicMatrix(left, right, top, bottom, near, far):
    """Build the orthographic matrix according to the formula:
    2 / (r - l)      , 0.0               , 0.0                 , 0.0
    0.0              , 2 / (t - b)       , 0.0                 , 0.0
    0.0              , 0.0               , 1 / (near - far)    , 0.0
    (l + r) / (l - r), (t + b) / (b - t) , near / (near - far) , 1.0
    """
    pMatrix = np.array([[2 / (right - left), 0.0, 0.0, 0.0],
                        [0.0, 2 / (top - bottom), 0.0, 0.0],
                        [0.0, 0.0, 1 / (near - far), 0.0],
                        [(left + right) / (left - right), (top + bottom) / (bottom - top), near / (near - far), 1.0]], np.float32)
    return pMatrix


def m3dLookAt(eye, target, up):
    """Define view matrix: eye - eye position (x, y, z), target - position where eye is looking, up - normal vector definition."""
    resVec = eye - target
    resVec = resVec / np.linalg.norm(resVec)
    mz = [*resVec]  # inverse line of sight
    mx = np.cross(up, mz)
    my = np.cross(mz, mx)
    tx = np.dot(mx, eye)
    ty = np.dot(my, eye)
    tz = -np.dot(mz, eye)
    return np.array([mx[0], my[0], mz[0], tx, mx[1], my[1], mz[1], ty, mx[2], my[2], mz[2], tz, 0, 0, 0, 1], dtype=np.float64).reshape((4, 4))


def GL_version():
    renderer = glGetString(GL_RENDERER)
    vendor = glGetString(GL_VENDOR)
    version = glGetString(GL_VERSION)

    return vendor.decode(), renderer.decode(), version.decode()


class VROpenGL:
    """Class for visualisation VASP and not only VASP calculation results. Have many features connected with bonds,
    cell and axes drawing and others options."""
    __defaultDisplay = (1000, 750)
    __lightVariables = (GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3, GL_LIGHT4, GL_LIGHT5, GL_LIGHT6, GL_LIGHT7)
    __lightStates = {i: False for i in range(8)}
    __lightPositions = [[10, 10, 10], [10, 10, -10], [10, -10, 10], [10, -10, -10], [-10, 10, 10], [-10, 10, -10],
                         [-10, -10, 10], [-10, -10, -10]]
    __viewAxes = True
    __viewCellBorder = True
    __drawType = GL_TRIANGLES
    __calculation = dict()
    # __primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Cube(__drawType)}
    # __primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Sphere(1, 32, 32)}
    __primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Quad(1.0)}
    _backgroundColor = (0.6, 0.6, 0.6, 1.0)
    __lightsDefault = [[10, 10, 10, 0.0], [-10, -10, 10, 1.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0]]
    __intensities = [[0.4, 0.4, 0.4], [0.4, 0.4, 0.4], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    __Kd = np.array([0.3, 0.3, 0.3], np.float32)
    __Ld = np.array([0.7, 0.7, 0.7], np.float32)
    __Ka, __Ks, __Shininess = np.array([0.5, 0.5, 0.5], dtype=np.float32), np.array([0.8, 0.8, 0.8], dtype=np.float32), 32.0
    __eyePosition = np.array([0.0, 20.0, 0.0])
    _fogColor = (0.6, 0.6, 0.6, 1.0)
    _defaultBondLength = 1.8
    _defaultBondRadius = 0.2

    @sendDataToLogger
    def __init__(self, app=None, settings=None, visualWindow=None, printWindow=None):
        """Initialization function of VROpenGL"""
        self.__settingsObject = settings
        self.__visualWindow = visualWindow
        self.__logger = printWindow
        self._parentWindowClosed = False
        self.__app = app
        self.__projectDirectory = self.__logger.getProjectDir()

        self.__display, self.windowSize = list(self.__defaultDisplay), list(self.__defaultDisplay)
        self.__viewMatrix = m3dLookAt(self.__eyePosition, np.array([0.0, 0.0, 0.0]), np.array([0.0, 0.0, 1.0]))
        self.__perspectiveMatrix = buildProjectionMatrix(self.__display[0], self.__display[1], 0, 45, 0.1, 60)
        self.__orthographicMatrix = buildOrthographicMatrix(-12, 12, 9, -9, 0.1, 60)
        self.__projectionMatrix = self.__perspectiveMatrix
        self._xD, self._yD, self._zD, self._scaleParameter = 0.0, 0.0, 0.0, 1.0
        self.rotationMatrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                         [0.0, 0.0, 1.0, 0],
                                         [0.0, -1.0, 0.0, 0.0],
                                         [self._xD, self._yD, self._zD, self._scaleParameter]],
                                        dtype=np.float64)
        self.__translationMatrix = np.array([[1.0, 0.0, 0.0, 0.0],
                                              [0.0, 1.0, 0.0, 0.0],
                                              [0.0, 0.0, 1.0, 0.0],
                                              [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        self.__lights = np.dot(np.asarray(self.__lightsDefault), self.rotationMatrix)
        self.modelViewMatrix, self.normalMatrix = None, None
        self.mousePressed, self.BackStep, self.ForwardStep, self.onlyKeyboardSelect, self.drawCell, self.drawAxes, self.isPerspective = False, False, True, True, True, True, True
        self.displayScaling, self._step, self._speed, self._fogMinDist, self._fogMaxDist, self._fogPower, self._fogDensity = 1.0, 0, 1, 0.1, 60, 1, 0.05
        self._setIDMode, self._setBondMode, self._setValenceMode = False, False, False
        self.newCoordinateStart = [0, 0]
        self.rotationInfo, self.defaultCubePosition = np.array([0.0, 0.0]), [[0, 0, 0]]
        self._BuffersLabels = []
        self.__cellPosition = self.__eyePosition.copy()
        self._BondRadius, self._BondLength, self._allBondsCalculate, self._BondsInfo = None, None, True, dict()
        self._cubeCoveredTexture, self._cubeCoveredTexture_sampler = None, None
        self.__isCalculationLoaded = False
        environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.init()
        try:
            self.__winIcon = self.__projectDirectory + r'\VR_icons\VR-logo.png'
            pygame.display.set_icon(pygame.image.load(self.__winIcon))
        except FileNotFoundError:
            pass
        pygame.display.set_caption('VaspReader')
        self.__scree = pygame.display.set_mode(self.__defaultDisplay, DOUBLEBUF | OPENGL | pygame.RESIZABLE)

        glMatrixMode(GL_PROJECTION)
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)

        vendor, renderer, version = GL_version()
        self.getLogger().addMessage(f"GL Vendor version: {vendor}", self.__class__.__name__)
        self.getLogger().addMessage(f"GL Renderer version: {renderer}", self.__class__.__name__)
        self.getLogger().addMessage(f"GL Version: {version}", self.__class__.__name__)
        self.getLogger().addMessage(f"Pygame Version: {pygame.__version__}\n", self.__class__.__name__)

        gluPerspective(45, (self.__defaultDisplay[0] / self.__defaultDisplay[1]), 0.1, 60.0)
        gluLookAt(0, 20, 0, 0, 0, 0, 0, 0, 1)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        self.__DisplayCenter = [self.__scree.get_size()[i] // 2 for i in range(2)]
        pygame.mouse.set_pos(self.__DisplayCenter)
        self.__program = VRShaders(self.__projectDirectory + '\\Visual\\Shaders', [r'vertex_shader.glsl', r'fragment_shader.glsl'], ['VERTEX', 'FRAGMENT'])
        # self.__axesPrimitives = [Primitives(1.0, [i, j, k]).Tube(1.0, 1.0, 64)]
        self._VBOBuffers = [VRVBO(self.__primitives['Primitive'][:-1], self.__primitives['Primitive'][-1]).createVaoBuffer()]
        self.loadTexture()

    def getLogger(self):
        return self.__logger

    def addMessage(self, message, fromWindow=None, operation=None, operationType='user', result='SUCCESS', cause=None, detailedDescription=None):
        if fromWindow is None:
            fromWindow = self.__class__.__name__
        self.__logger.addMessage(message, fromWindow, operation, operationType, result, cause, detailedDescription)

    @sendDataToLogger
    def hide(self):
        self.__scree = pygame.display.set_mode(self.__display, DOUBLEBUF | OPENGL | pygame.RESIZABLE | pygame.HIDDEN)

    @sendDataToLogger
    def show(self):
        self.__scree = pygame.display.set_mode(self.__display, DOUBLEBUF | OPENGL | pygame.RESIZABLE)

    @sendDataToLogger
    def change_light(self, lightVariableNumber, lightPosition):
        self.__lightStates[lightVariableNumber] = not self.__lightStates[lightVariableNumber]
        if self.__lightStates[lightVariableNumber]:
            glEnable(self.__lightVariables[lightVariableNumber])
            glLight(self.__lightVariables[lightVariableNumber], GL_POSITION, (*lightPosition, 1))
            glLightfv(self.__lightVariables[lightVariableNumber], GL_AMBIENT, [0.1, 0.1, 0.1, 1])
            glLightfv(self.__lightVariables[lightVariableNumber], GL_DIFFUSE, [1, 1, 1, 1])
            glLightfv(self.__lightVariables[lightVariableNumber], GL_SPECULAR, [1, 1, 1, 1])
        else:
            glDisable(self.__lightVariables[lightVariableNumber])

    @sendDataToLogger
    def findWindowDimensions(self, far):
        far = 20 + far
        xLimit = np.sin(np.pi / 16 * 3) * far
        yLimit = xLimit / 4 * 3
        if self.windowSize[0] / 4 < self.windowSize[1] / 3:
            xLimit = xLimit * (self.windowSize[0] / self.__display[0])
        else:
            yLimit = yLimit * (self.windowSize[1] / self.__display[1])
        return xLimit, yLimit, -(far - 20)

    @sendDataToLogger
    def changeLightPosition(self, newPosition, lightIndex):
        self.__lightPositions[lightIndex] = newPosition

    @sendDataToLogger(operationType='user')
    def displayResize(self, event):
        self.__display = [int(event.w), int(event.h)]
        self.windowSize = [int(event.w), int(event.h)]
        difference = [int(self.__display[i] - self.__defaultDisplay[i]) for i in range(2)]
        if difference[0] > difference[1]:
            self.__display[1] = self.__defaultDisplay[1] + int(difference[0] * 3 / 4)
        elif difference[0] < difference[1]:
            self.__display[0] = self.__defaultDisplay[0] + int(difference[1] * 4 / 3)
        self.displayScaling = self.__display[0] / self.__defaultDisplay[0]

        nlw = (event.w - self.__display[0]) // 2
        nlh = (event.h - self.__display[1]) // 2

        self._displayCenter = [event.w // 2, event.h // 2]
        self.newCoordinateStart = [nlw, nlh]
        glViewport(nlw, nlh, self.__display[0], self.__display[1])

    @sendDataToLogger
    def loadCalculationInfo(self, calculation):
        self.__calculation = calculation
        self.__isCalculationLoaded = True

    def completeLoadOfCalculation(self):
        self.__primitives.clear()
        self._VBOBuffers.clear()
        self._BuffersLabels.clear()
        self.__cellPosition[1] = self.__calculation['BASIS_VERT'].max()
        for _, atom in enumerate(self.__calculation['ATOMSINFO']):
            self.__primitives[atom] = Primitives(1, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Sphere(self.__calculation['ATOMSINFO'][atom]['RADII'], 32, 32)
            self.__primitives[f'{atom}_Sel'] = Primitives(1, self.__calculation['ATOMSINFO'][atom]['COLORVALUE'] * 0.6).Sphere(self.__calculation['ATOMSINFO'][atom]['RADII'] * 1.15, 32, 32)
        for _, key in enumerate(self.__primitives):
            self._VBOBuffers.append(VRVBO(self.__primitives[key][:-1], self.__primitives[key][-1]).createVaoBuffer())
            self._BuffersLabels.append(key)
        self.__isCalculationLoaded = False

    @sendDataToLogger
    def withoutCalculation(self):
        self.__calculation = None
        self.__primitives.clear()
        self._VBOBuffers.clear()
        self._BuffersLabels.clear()
        self.__cellPosition[1] = self._fogMaxDist = 20
        self.__primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Quad(1.0)}
        # self.__primitives = {'Primitive': Primitives(3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Cube(self.__drawType)}
        self._VBOBuffers.append(VRVBO(self.__primitives['Primitive'][:-1], self.__primitives['Primitive'][-1]).createVaoBuffer())

    @sendDataToLogger
    def setDefaultRotationMatrix(self):
        self.rotationMatrix = self.rotationMatrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                                                [0.0, 0.0, 1.0, 0],
                                                                [0.0, -1.0, 0.0, 0.0],
                                                                [self._xD, self._yD, self._zD, self._scaleParameter]], dtype=np.float64)

    def cellDraw(self, cell, drawCell=False, drawAxes=False, lineWidth=3):
        """Draw cell of model."""
        edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7), (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7)) if not drawAxes else ((0, 1), (0, 4), (2, 1), (2, 7), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))
        glLineWidth(lineWidth)
        glBegin(GL_LINES)
        if drawCell:
            for edge in edges:
                for vertex in edge:
                    glColor4f(1.0, 1.0, 0.0, 1.0)
                    glVertex3fv(cell[vertex])
        if drawAxes:
            for color, edge in [((1.0, 0.0, 0.0), (3, 6)), ((0.0, 1.0, 0.0), (3, 0)), ((0.0, 0.0, 1.0), (3, 2))]:
                glColor4f(*color, 1.0)
                glVertex3fv(cell[edge[0]])
                glVertex3fv(cell[edge[1]])
        glEnd()

    @sendDataToLogger
    def loadTexture(self):  # , texture
        image = Image.open(self.__projectDirectory + r'VR_icons\VR-logo.png')
        image = image.convert("RGBA")

        imgData = image.tobytes()

        self._cubeCoveredTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._cubeCoveredTexture)
        # self._cubeCoveredTexture_sampler = glGenSamplers(1)
        # glBindSampler(self._cubeCoveredTexture, self._cubeCoveredTexture_sampler)


        # Set the texture wrapping parameters

        # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        color = [1.0, 1.0, 1.0, 1.0]
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, color)

        # Set texture filtering parameters

        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, imgData)
        glGenerateMipmap(GL_TEXTURE_2D)
        # print(glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE))
        glBindTexture(GL_TEXTURE_2D, 0)


    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def defineRotationAroundAxes(xD, yD, zD, scaleParameter, xR, yR, zR, limit_rotations=True):
        if limit_rotations:
            xR, yR, zR = xR % 360 - 180, yR % 360 - 180, zR % 360 - 180
        xRotation = np.array([[1.0, 0.0, 0.0, 0.0],
                               [0.0, np.cos(np.radians(xR)), -np.sin(np.radians(xR)), 0.0],
                               [0.0, np.sin(np.radians(xR)), np.cos(np.radians(xR)), 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        yRotation = np.array([[np.cos(np.radians(yR)), 0.0, np.sin(np.radians(yR)), 0.0],
                               [0.0, 1.0, 0.0, 0.0],
                               [-np.sin(np.radians(yR)), 0.0, np.cos(np.radians(yR)), 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        zRotation = np.array([[np.cos(np.radians(zR)), -np.sin(np.radians(zR)), 0.0, 0.0],
                               [np.sin(np.radians(zR)), np.cos(np.radians(zR)), 0.0, 0.0],
                               [0.0, 0.0, 1.0, 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        matrix = np.dot(zRotation, np.dot(yRotation, xRotation))
        matrix[3][0], matrix[3][1], matrix[3][2] = xD, yD, zD
        matrix[3][3] = scaleParameter
        return matrix

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def defineRotation(defineRotationFunction, rotationMatrix, rotationInfo, xD, yD, zD, scaleParameter):
        if rotationInfo[0] or rotationInfo[1] or xD or yD or zD or scaleParameter - 1.0:
            rotationMatrix = np.dot(rotationMatrix, defineRotationFunction(xD, yD, zD, scaleParameter, rotationInfo[1], 0, rotationInfo[0]))
            # self.__lights = np.dot(np.asarray(self.__lightsDefault), self.rotationMatrix)
        return rotationMatrix

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def defineNormalMatrix(viewMatrix, rotationMatrix):
        modelViewMatrix = np.dot(viewMatrix, rotationMatrix.transpose())
        return np.linalg.inv(modelViewMatrix[:3, :3]).transpose()

    @sendDataToLogger(operationType='user')
    def selectAtom(self, select):
        self.BackStep, self.ForwardStep = False, False
        mouseClick = pygame.mouse.get_pos()
        mouseClick = [mouseClick[i] - self.newCoordinateStart[i] for i in range(2)]
        if self.isPerspective:
            prjMat = (GLfloat * 16)()
            glGetFloatv(GL_PROJECTION_MATRIX, prjMat)
            prjMat = np.dot(self.rotationMatrix, np.array(prjMat).reshape((4, 4))).reshape((16, 1))
            onRect = perspectiveChoose(prjMat, mouseClick, self.__calculation['POSITIONS'][self._step], self.__display, self.__calculation['RADII'])
        else:
            coordinates = (np.dot(self.__calculation['POSITIONS'][self._step], self.rotationMatrix[:3, :3]) + np.array([[*self.rotationMatrix[3, :3]] for _ in range(self.__calculation['POSITIONS'][self._step].shape[0])])) / self.rotationMatrix[-1, -1]
            onRect = orthographicChoose(mouseClick, coordinates, self.__display, self.__calculation['RADII'])
        alreadySelected = False
        if select:
            for num, selected in enumerate(onRect):
                if selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] != 'Sel' and not (self._setIDMode or self._setBondMode or self._setValenceMode):
                    self.__calculation['ATOMNAMES'][num] += '_Sel'
                elif selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] == 'Sel':
                    alreadySelected = True
        else:
            for num, selected in enumerate(onRect):
                if selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] == 'Sel' and not (self._setIDMode or self._setBondMode or self._setValenceMode):
                    self.__calculation['ATOMNAMES'][num] = self.__calculation['ATOMNAMES'][num][:-4]
                elif selected and self.__calculation['ATOMNAMES'][num].split('_')[-1] != 'Sel':
                    alreadySelected = True
        if alreadySelected:
            self.getLogger().addMessage('This atom was already chose.' if select else 'This atom was already deleted.', self.__class__.__name__)
        pygame.time.wait(200)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def nonoptimalDimensionSearch(positions, numberOfDividings):
        length = len(positions) - 1
        sizeArray = np.zeros((3, numberOfDividings + 1))
        deltaDim = np.zeros(3)
        for iteration in range(numberOfDividings + 1):
            step = iteration * length // numberOfDividings
            pos = positions[step].transpose()
            sizeArray[0] = pos[0].max() - pos[0].min()
            sizeArray[1] = pos[1].max() - pos[1].min()
            sizeArray[2] = pos[2].max() - pos[2].min()
        sizeArray = np.asarray(sizeArray)
        for index in range(3):
            deltaDim[index] = sizeArray[index].max() - sizeArray[index].min()
        return deltaDim.argsort()[-2]

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighboursSearchBody(num, index, positions, indexes, dimension, bondLength):
        highestIndex = maxIndex = len(indexes) - num
        minIndex = 0
        nowIndex = maxIndex // 2 if not maxIndex % 2 else maxIndex // 2 + 1
        pos = positions[index][dimension]
        while True:
            indexComp = indexes[nowIndex - 1 + num]
            indexCompNext = indexes[nowIndex + num]
            statement1 = abs(pos - positions[indexComp][dimension]) <= bondLength
            statement2 = abs(pos - positions[indexCompNext][dimension]) <= bondLength
            if statement1 and not statement2:
                break
            elif nowIndex == highestIndex - 1 and statement1 and statement2:
                nowIndex = highestIndex
                break
            elif nowIndex == 0 and not statement1:
                break
            elif statement1 and statement2:
                minIndex = nowIndex
                summary = nowIndex + maxIndex
                nowIndex = summary // 2 if not summary % 2 else summary // 2 + 1
            else:
                maxIndex = nowIndex
                summary = nowIndex + minIndex
                nowIndex = summary // 2 if not summary % 2 else summary // 2 + 1
        trackingPos = positions[index]
        returningIndexes = []
        for anotherIndex in indexes[num + 1:nowIndex + num]:
            targetPos = positions[anotherIndex]
            length = np.linalg.norm(trackingPos - targetPos)
            if length <= bondLength:
                returningIndexes.append(anotherIndex)
        return np.array(returningIndexes)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighboursSearch(searchAlgoritm, positions, indexes, dimension, bondLength):
        neighbours = dict()
        indexesCp = indexes[:-1]
        for num, index in enumerate(indexesCp):
            neighbours[int(index)] = searchAlgoritm(num, index, positions, indexes, dimension, bondLength)
        return neighbours

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighboursSearchBetweenTypesBody(index, positions, indexes, dimension, bondLength):
        highestIndex = maxIndex = len(indexes)
        minIndex = 0
        nowIndex = maxIndex // 2 if not maxIndex % 2 else maxIndex // 2 + 1
        pos = positions[index][dimension]
        while True:
            indexComp = indexes[nowIndex - 1]
            indexCompNext = indexes[nowIndex]
            statement1 = abs(pos - positions[indexComp][dimension]) <= bondLength
            statement2 = abs(pos - positions[indexCompNext][dimension]) <= bondLength
            if statement1 and not statement2:
                break
            elif nowIndex == highestIndex - 1 and statement1 and statement2:
                nowIndex = highestIndex
                break
            elif nowIndex == 0 and not statement1:
                break
            elif statement1 and statement2:
                minIndex = nowIndex
                summary = nowIndex + maxIndex
                nowIndex = summary // 2 if not summary % 2 else summary // 2 + 1
            else:
                maxIndex = nowIndex
                summary = nowIndex + minIndex
                nowIndex = summary // 2
        trackingPos = positions[index]
        returningIndexes = []
        for anotherIndex in indexes[:nowIndex]:
            targetPos = positions[anotherIndex]
            length = np.linalg.norm(trackingPos - targetPos)
            if length <= bondLength:
                returningIndexes.append(anotherIndex)
        return np.array(returningIndexes)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighboursSearchBetweenTypes(searchAlgoritm, positions, indexes_type1, indexesType2, dimension, bondLength):
        neighbours = dict()
        for _, index in enumerate(indexes_type1):
            neighbours[int64(index)] = searchAlgoritm(index, positions, indexesType2, dimension, bondLength)
        return neighbours

    def calculateBonds(self):  # необходимо отсортировать массив по x, y, z и смотреть начиная с какого то элемента массива расстояние. Если оно больше заданного, то не включаем в рассмотрение, если меньше, то включаем и при этом соответствующим образом сдвигаем далее индекс поиска
        oneStepPositions = self.__calculation['POSITIONS'][self._step]
        biggestDim = self.nonoptimalDimensionSearch(self.__calculation['POSITIONS'], 9)
        if self._allBondsCalculate:
            oneStepPositionsTr = oneStepPositions.transpose()
            indexesBig = oneStepPositionsTr[biggestDim].argsort()
            neighbours = self.neighboursSearch(self.neighboursSearchBody, oneStepPositions, indexesBig, biggestDim, self._BondLength)
        else:
            type1, type2 = 'Mo', 'S'
            indexes1, indexes2 = self.__calculation['ATOM-NUMBERS'][type1], self.__calculation['ATOM-NUMBERS'][type2]
            oneStepPositionsType2 = oneStepPositions[indexes2]
            oneStepPositionsTr = oneStepPositionsType2.transpose()
            indexesBig = oneStepPositionsTr[biggestDim].argsort() + min(indexes2)
            neighbours = self.neighboursSearchBetweenTypes(self.neighboursSearchBetweenTypesBody, oneStepPositions, indexes1, indexesBig, biggestDim, self._BondLength)

    def prepareBondBuffers(self):
        atoms = self.__calculation['ATOMNAMES']
        if self._BondRadius is None and self._BondLength is None:
            for atom in set(atoms):
                self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._defaultBondRadius, self._defaultBondLength / 2, 32)
        else:
            for atom in set(atoms):
                self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._BondRadius[f'{atom}_Bond'], self._BondLength[f'{atom}_Bond'] / 2, 32)
        for key in set(atoms):
            self._VBOBuffers.append(VRVBO(self.__primitives[key + '_Bond'][:-1], self.__primitives[key + '_Bond'][-1]).createVaoBuffer())
            self._BuffersLabels.append(key + '_Bond')

    @sendDataToLogger
    def mainloop(self):
        targetFps = 60
        prevTime = time.time()
        run = True

        while run:
            if self.__isCalculationLoaded:
                self.completeLoadOfCalculation()
            # glLoadIdentity()
            # glMultMatrixf(self.rotationMatrix)
            if self.isPerspective:
                self.__projectionMatrix = self.__perspectiveMatrix
            else:
                self.__projectionMatrix = self.__orthographicMatrix
            if self._parentWindowClosed:
                break
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.BackStep, self.ForwardStep = False, False
                    run = False
                    self.__app.closeAllWindows()
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.BackStep, self.ForwardStep = False, False
                        run = False
                        self.__app.closeAllWindows()
                        break
                    if event.key == pygame.K_F4:
                        raise KeyError("Pushed exit key. Don't push F4 if you don't want to exit program.")
                if event.type == pygame.MOUSEMOTION and event.type != pygame.WINDOWLEAVE:
                    coord_x, coord_y = pygame.mouse.get_pos()
                    coord_x_mouse, coord_y_mouse = pygame.mouse.get_rel()
                    if self.mousePressed:
                        self.BackStep, self.ForwardStep = False, False
                        if self.onlyKeyboardSelect:
                            pygame.mouse.set_visible(False)
                        self.rotationInfo[0] -= (event.rel[0]) * 0.4
                        self.rotationInfo[1] += (event.rel[1]) * 0.4
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.onlyKeyboardSelect:
                        pygame.mouse.set_visible(True)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                    self._scaleParameter = self._scaleParameter * 0.92
                    pygame.time.wait(10)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                    self._scaleParameter = self._scaleParameter * 1.08
                    pygame.time.wait(10)
                if event.type == pygame.MOUSEBUTTONDOWN and self._BuffersLabels:
                    if event.button == 1:
                        if not self.onlyKeyboardSelect:
                            self.selectAtom(True)
                    if event.button == 3:
                        if not self.onlyKeyboardSelect:
                            self.selectAtom(False)

                if event.type == pygame.VIDEORESIZE:
                    self.displayResize(event)

            keypress = pygame.key.get_pressed()

            # Отдаление модели при нажатии клавиши - на кейпаде
            if keypress[pygame.K_KP_MINUS] or keypress[pygame.K_MINUS]:
                self.BackStep, self.ForwardStep = False, False
                self._scaleParameter = self._scaleParameter * 1.03
                pygame.time.wait(10)
            # Приближение модели при нажатии кнопки + на кейпаде
            if keypress[pygame.K_KP_PLUS] or keypress[pygame.K_EQUALS]:
                self.BackStep, self.ForwardStep = False, False
                self._scaleParameter = self._scaleParameter * 0.97
                pygame.time.wait(10)
            ##################################
            if keypress[pygame.K_BACKSPACE]:
                self.BackStep, self.ForwardStep = False, False
                self.rotationInfo[0], self.rotationInfo[1] = 0.0, 0.0
                self._xD, self._yD, self._zD = 0, 0, 0
                self._scaleParameter = 1.0
                self.setDefaultRotationMatrix()
                self.__lights = np.dot(np.asarray(self.__lightsDefault), self.rotationMatrix)

            if keypress[pygame.K_LEFT]:
                self.BackStep, self.ForwardStep = False, False
                self.rotationInfo[0] -= 1.5
            if keypress[pygame.K_RIGHT]:
                self.BackStep, self.ForwardStep = False, False
                self.rotationInfo[0] += 1.5
            if keypress[pygame.K_UP]:
                self.BackStep, self.ForwardStep = False, False
                self.rotationInfo[1] += 1.5
            if keypress[pygame.K_DOWN]:
                self.BackStep, self.ForwardStep = False, False
                self.rotationInfo[1] -= 1.5
            if keypress[pygame.K_z]:
                self._xD = self._xD - 0.1
            if keypress[pygame.K_x]:
                self._xD = self._xD + 0.1
            if keypress[pygame.K_j]:
                self._zD = self._zD + 0.1
            if keypress[pygame.K_u]:
                self._zD = self._zD - 0.1
            if keypress[pygame.K_i]:
                self._fogPower += 1
                time.sleep(0.08)
            if keypress[pygame.K_k]:
                if self._fogPower > 1:
                    self._fogPower -= 1
                    time.sleep(0.08)
            if keypress[pygame.K_o]:
                self._fogDensity = self._fogDensity * 1.05
                time.sleep(0.08)
            if keypress[pygame.K_l]:
                self._fogDensity = self._fogDensity / 1.05
                time.sleep(0.08)

            if (keypress[pygame.K_COMMA] or self.BackStep) and self._BuffersLabels:
                self._step -= 1 * self._speed
                if self._step < 0:
                    self._step = self.__calculation['STEPS'] - 1 + self._step
                self.__visualWindow.StepSlider.setSliderPosition(self._step)
                self.BackStep = True
            if (keypress[pygame.K_PERIOD] or self.ForwardStep) and self._BuffersLabels:
                self._step += 1 * self._speed
                if self._step >= self.__calculation['STEPS']:
                    self._step = self._step - self.__calculation['STEPS']
                self.__visualWindow.StepSlider.setSliderPosition(self._step)
                self.ForwardStep = True

            if keypress[pygame.K_a]:
                self.selectAtom(True)
            if keypress[pygame.K_d]:
                self.selectAtom(False)

            if keypress[pygame.K_p]:
                self.__visualWindow.processingStart()

            # Движение модели мышкой
            for _ in pygame.mouse.get_pressed():
                if pygame.mouse.get_pressed()[0] == 1:
                    self.mousePressed = True
                elif pygame.mouse.get_pressed()[0] == 0:
                    self.mousePressed = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(*self._backgroundColor)
            self.rotationMatrix = self.defineRotation(self.defineRotationAroundAxes, self.rotationMatrix, self.rotationInfo, self._xD, self._yD, self._zD, self._scaleParameter)
            self.normalMatrix = self.defineNormalMatrix(self.__viewMatrix, self.rotationMatrix)
            # # Отрисовка границ ячейки
            # if self.drawCell and self._BuffersLabels:
            #     self.cellDraw(self.__calculation['BASIS_VERT'], self.drawCell, self.drawAxes, 3)

            # x, y, z = self.findWindowDimensions(-5)
            for index, Buffer in enumerate(self._VBOBuffers):
                Buffer.prepareToDraw(self.__program.program)
                Buffer.setLightSettings(self.__program.uniformVariablesDict, self.__Ka, self.__Kd, self.__Ks, self.__Shininess, self.__lights, self.__intensities)
                Buffer.setFogParameters(self.__program.uniformVariablesDict, self.__cellPosition, self._fogColor, self._fogMinDist, self._fogMaxDist, self._fogPower, self._fogDensity)
                if not self._BuffersLabels:
                    glActiveTexture(GL_TEXTURE0)
                    glBindTexture(GL_TEXTURE_2D, self._cubeCoveredTexture)
                    Buffer.isTextureExist(self.__program.uniformVariablesDict, 1)
                    Buffer.setTextureInfo(self.__program.uniformVariablesDict, 0)
                    for xD, yD, zD in self.defaultCubePosition:
                        self.__translationMatrix[0][-1] = xD
                        self.__translationMatrix[1][-1] = yD
                        self.__translationMatrix[2][-1] = zD
                        Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
                    glBindTexture(GL_TEXTURE_2D, 0)
                else:
                    Buffer.isTextureExist(self.__program.uniformVariablesDict, 0)
                    for atomIndex, (xD, yD, zD) in enumerate(self.__calculation['POSITIONS'][self._step]):
                        if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex]:
                            self.__translationMatrix[0][-1] = xD
                            self.__translationMatrix[1][-1] = yD
                            self.__translationMatrix[2][-1] = zD
                            Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
                        if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex] + '_Bond':
                            self.__translationMatrix[0][-1] = xD
                            self.__translationMatrix[1][-1] = yD
                            self.__translationMatrix[2][-1] = zD
                            Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
                Buffer.endOfDrawing()
            pygame.display.flip()
            self.rotationInfo[0], self.rotationInfo[1] = 0.0, 0.0
            self._scaleParameter = 1.0
            self._xD, self._yD, self._zD = 0.0, 0.0, 0.0
            currTime = time.time()
            diff = currTime - prevTime
            delay = max(1.0 / targetFps - diff, 0)
            time.sleep(delay)
            fps = 1.0 / (delay + diff)
            prevTime = currTime
        for _ in range(len(self._VBOBuffers)):
            self._VBOBuffers.pop(0).__del__()
        self.__visualWindow.close()
        pygame.quit()
