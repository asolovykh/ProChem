import numpy as np
import os
import random
import time
import logging
from numba import jit
from numba.core.types import int64
from PIL import Image
import OpenGL
from OpenGL.GL import *
from PySide6.QtCore import QThread, QTimer
from PySide6.QtGui import QOpenGLContext, QSurfaceFormat
from Gui.VROpenGLGUI import Ui_VROpenGL, QMainWindow
from Visual.VRPrimitives import Primitives
from Visual.VRVBO import VRVBO
from Visual.Shaders.VRShaders import VRShaders
OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)


def transform_vec3(vec_a, mat44) -> tuple[list[float], int]:
    """Transform 3d vector to 2d projection."""
    vec_b = [0, 0, 0, 0]
    for i in range(0, 4):
        vec_b[i] = vec_a[0] * mat44[0 * 4 + i] + vec_a[1] * mat44[1 * 4 + i] + vec_a[2] * mat44[2 * 4 + i] + mat44[3 * 4 + i]
    return [vec_b[0] / vec_b[3], vec_b[1] / vec_b[3], vec_b[2] / vec_b[3]], vec_b[3]


def perspective(fovy, aspect, znear, zfar):
    f = 1.0 / np.tan(np.radians(fovy) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (zfar + znear) / (znear - zfar)
    m[2, 3] = (2 * zfar * znear) / (znear - zfar)
    m[3, 2] = -1.0
    return m


def ortho(left, right, top, bottom, near, far):
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


def look_at(eye, center, up):
    f = center - eye
    f = f / np.linalg.norm(f)
    u = up / np.linalg.norm(up)
    s = np.cross(f, u)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0, 0:3] = s
    m[1, 0:3] = u
    m[2, 0:3] = -f
    trans = np.identity(4, dtype=np.float32)
    trans[0, 3] = -eye[0]
    trans[1, 3] = -eye[1]
    trans[2, 3] = -eye[2]
    return m @ trans


def perspective_choose(prj_mat, mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with perspective view.
       prjMat - projection matrix, mpos - mouse position at the screen,
       ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    ll_ndc = [[0.0 for i in range(3)] for m in range(len(ll))]
    in_rect_counter = 0  # atoms in sphere counter
    depth = list()  # atoms in sphere list
    mult = [0.0 for _ in range(len(ll))]  # коэффициенты масштабирования пространства
    for num in range(len(ll)):
        ll_ndc[num], mult[num] = transform_vec3(ll[num], prj_mat)  # координаты в мировом пространстве???
    radii = [parameter[i] / mult[i] * 1.0 for i in range(len(ll))]  # radius of projected sphere
    ndc = [2.0 * mpos[0] / dis[0] - 1.0, 1.0 - 2.0 * mpos[1] / dis[1]]
    in_rect = [0 for _ in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if ll_ndc[num][0] - radii[num] <= ndc[0] <= ll_ndc[num][0] + radii[num] and ll_ndc[num][1] - radii[num] <= ndc[1] <= ll_ndc[num][1] + radii[num]:
            in_rect[num] = 1
        else:
            in_rect[num] = 0
    for num in range(len(ll)):
        if in_rect[num] == 1:
            in_rect_counter += 1  # число попаданий
            depth.append(ll_ndc[num][2])  # координаты по глубине
    if in_rect_counter > 1:
        right_vec = min(depth)
        for num in range(len(ll)):
            if ll_ndc[num][2] != right_vec:
                in_rect[num] = 0
    return in_rect


def orthographic_choose(mpos, ll, dis, parameter) -> list[int]:
    """Option of choosing object on the screen with orthographic view.
    mpos - mouse position at the screen, ll - atoms vertices, dis - display size, parameter - radii of sphere."""
    ortho_size = (12, 9)
    coordinate = [(1.0 - 2.0 * mpos[0] / dis[0]) * ortho_size[0], (1.0 - 2.0 * mpos[1] / dis[1]) * ortho_size[1]]
    in_rect_counter = 0  # atoms in sphere counter
    depth = []  # atoms in sphere list
    in_rect = [0 for m in range(len(ll))]  # список попаданий в атом, 0 - не попал, 1 - попал
    for num in range(len(ll)):
        if ll[num][0] - parameter[num] <= coordinate[0] <= ll[num][0] + parameter[num] and ll[num][2] - parameter[num] <= coordinate[1] <= ll[num][2] + parameter[num]:
            in_rect[num] = 1
        else:
            in_rect[num] = 0
    for num in range(len(ll)):
        if in_rect[num] == 1:
            in_rect_counter += 1  # число попаданий
            depth.append(ll[num][1])  # координаты по глубине
    if in_rect_counter > 1:
        right_vec = max(depth)
        for num in range(len(ll)):
            if ll[num][1] != right_vec:
                in_rect[num] = 0
    return in_rect


def rotate_y(angle_deg):
    a = np.radians(angle_deg)
    c = np.cos(a)
    s = np.sin(a)
    m = np.identity(4, dtype=np.float32)
    m[0, 0] = c
    m[0, 2] = s
    m[2, 0] = -s
    m[2, 2] = c
    return m


class VROpenGL(Ui_VROpenGL, QMainWindow):
    """Class for visualisation VASP and not only VASP calculation results. Have many features connected with bonds,
    cell and axes drawing and others options."""
    __default_draw = GL_TRIANGLES
    __default_primitives = {'Quad': Primitives(5, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Quad(1.0),
                            'Sphere': Primitives(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Sphere(1, 32, 32),
                            'Torus': Primitives(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Torus(0.5, 1, 32, 32),
                            'Cube': Primitives(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]).Cube(__default_draw)}
    __calculation = dict()

    def __init__(self, settings=None, visual_window=None, print_window=None):
        """Initialization function of VROpenGL"""
        super(VROpenGL, self).__init__()
        self.__settings = settings
        self.__settings.set_scene_params((GL_LIGHT0, GL_LIGHT1, GL_LIGHT2, GL_LIGHT3, 
                                          GL_LIGHT4, GL_LIGHT5, GL_LIGHT6, GL_LIGHT7), 
                                         'light', 'variables')
        self.__settings.set_scene_params(self.__default_draw, 'draw', 'type')
        self.__visual_window = visual_window
        self.__print_window = print_window
        self._parent_window_closed = False
        self.__project_directory = self.__print_window.get_project_dir()
        
        self.setupUi(self)
        logger.info(f"OpenGL UI setuped")
        self.opengl_initialized = False 
        self.openGLWidget.initializeGL = self.initializeGL
        self.openGLWidget.resizeGL = self.resizeGL
        self.openGLWidget.paintGL = self.paintGL
        self.openGLWidget.setMouseTracking(True)
        self.openGLWidget.keyPressEvent = self.keyPressEvent
        logger.info(f"OpenGLWidget virtual methods initialized")
         
        self.__program = None
        self._VBOBuffers = None
        self.__primitives = self.__default_primitives

        self._x_d, self._y_d, self._z_d, self._scale_parameter = 0.0, 0.0, 0.0, 1.0
        self.__view_matrix = look_at(self.__settings.get_scene_params('view', 'eye_position'), np.array([0, 0, 0]), np.array([0, 1, 0]))
        #self.__view_matrix = look_at(np.array([4, 0, 0]), np.array([0, 0, 0]), np.array([0, 0, 1]))
        self.__perspective_matrix = perspective(45, self.openGLWidget.size().width() / self.openGLWidget.size().height(), 0.1, 100)
        self.__orthographic_matrix = ortho(-12, 12, 9, -9, 0.1, 60)
        self.__projection_matrix = self.__perspective_matrix
        self.rotation_matrix = np.identity(4, dtype=np.float32)
        #self.rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
        #                                 [0.0, 0.0, 1.0, 0],
        #                                 [0.0, -1.0, 0.0, 0.0],
        #                                 [0.0, 0.0, 0.0, 1.0]])
        self.__translation_matrix = np.identity(4, dtype=np.float32)
        self.__translation_matrix[0][-1] = self._x_d
        self.__translation_matrix[1][-1] = self._y_d
        self.__translation_matrix[2][-1] = self._z_d
        self.__translation_matrix[3][-1] = self._scale_parameter
        self.__normal_matrix = np.identity(3, dtype=np.float32) # glm.mat3(glm.transpose(glm.inverse(self.__view_matrix * self.rotation_matrix)))
        
        # print(self.__projection_matrix)
        # print(self.__view_matrix)
        # print(self.__translation_matrix * self.rotation_matrix)
        # print(self.__translation_matrix)
        # print(self.__projection_matrix * self.__view_matrix * self.rotation_matrix * self.__translation_matrix)
        # cube_points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 1.0], [0.0, 1.0, 1.0]])
        # for point in cube_points:
        #     print(self.__projection_matrix * self.__view_matrix * self.rotation_matrix * self.__translation_matrix * glm.vec4([*point, 1]))
        # print(self.__normal_matrix)
        # print(self.__primitives['Sphere'])

        self.mouse_pressed, self.back_step, self.forward_step = False, False, False
        self.mouse_x_position, self.mouse_y_position = 0, 0
        self.display_scaling, self._step  = 1.0, 0
        self._set_id_mode, self._set_bond_mode, self._set_valence_mode = False, False, False
        
        self.new_coordinate_start = [0, 0]
        self.rotation_angle = 0
        self.rotation_info, self.default_cube_position = np.array([0.0, 0.0]), [[0, 0, 0]]
        self._buffers_labels = []
        self.__cell_position = self.__settings.get_scene_params('view', 'eye_position').copy()
        self._bond_radius, self._bond_length, self._all_bonds_calculate, self._bonds_info = None, None, True, dict()
        self._cube_covered_texture, self._cube_covered_texture_sampler = None, None
        self.__is_calculation_loaded = False

        self.__lights = np.dot(np.asarray(self.__settings.get_scene_params('light', 'default')), self.rotation_matrix)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.openGLWidget.update)
        self.timer.start(16)
        logger.info(f"OpenGL window created")

    def get_default_format(self):
        format = QSurfaceFormat()
        format.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
        format.setVersion(4, 3) # Request OpenGL 4.3
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        format.setDepthBufferSize(24)
        return format

    def initializeGL(self):
        #self.openGLWidget.setFormat(self.get_default_format())
        # glMatrixMode(GL_PROJECTION)
        glEnable(GL_TEXTURE_2D)
        # glShadeModel(GL_SMOOTH)
         
        #gluPerspective(45, (self.openGLWidget.size().width() / self.openGLWidget.size().height()), 0.1, 60)
        #gluLookAt(0, 20, 0, 0, 0, 0, 0, 0, 1)
 
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
 
        # glMatrixMode(GL_MODELVIEW)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # glEnable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)

        # glViewport(0, 0, self.openGLWidget.size().width(), self.openGLWidget.size().height())

        self.__program = VRShaders(os.path.join(self.__project_directory, 'Visual', 'Shaders'), [r'vertex_shader.glsl', r'fragment_shader.glsl'], ['VERTEX', 'FRAGMENT'])
        self._VBOBuffers = [VRVBO(self.__primitives['Quad'][:-1], self.__primitives['Quad'][-1]).createVaoBuffer()]
        self.opengl_initialized = True
        logger.info(f"OpenGL initialized")
        self.load_texture()

    def resizeGL(self, w, h):
        # Update projection matrix and other size related settings:
        print(f"w: {w}, h: {h}")
        glViewport(0, 0, w, h)
        self.__perspective_matrix = perspective(45, w / h, 0.1, 100)
        self.__projection_matrix = self.__perspective_matrix
        
        # print(self.__projection_matrix)
        # print(self.__projection_matrix * self.__view_matrix * self.rotation_matrix * self.__translation_matrix * glm.vec4([1,1,1,1]))
        ...

    def paintGL(self): 
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if self.opengl_initialized:
            self.rotation_matrix = rotate_y(self.rotation_angle) # glm.rotate(self.rotation_matrix, glm.radians(1), glm.vec3(1, 1, 1))
            self.rotation_angle += 1
            for index, Buffer in enumerate(self._VBOBuffers):
                Buffer.prepareToDraw(self.__program.program)
                Buffer.setLightSettings(self.__program.uniformVariablesDict, 
                                        self.__settings.get_scene_params('light', 'ka'),
                                        self.__settings.get_scene_params('light', 'kd'),
                                        self.__settings.get_scene_params('light', 'ks'),
                                        self.__settings.get_scene_params('light', 'shininess'),
                                        self.__settings.get_scene_params('light', 'default'),
                                        self.__settings.get_scene_params('light', 'intensities'))
                # Buffer.setFogParameters(self.__program.uniformVariablesDict, 
                #                         self.__settings.get_scene_params('view', 'eye_position'),
                #                         self.__settings.get_scene_params('fog', 'color'),
                #                         self.__settings.get_scene_params('fog', 'min_dist'),
                #                         self.__settings.get_scene_params('fog', 'max_dist'),
                #                         self.__settings.get_scene_params('fog', 'power'),
                #                         self.__settings.get_scene_params('fog', 'density'))
                if not self._buffers_labels:
                    glActiveTexture(GL_TEXTURE0)
                    glBindTexture(GL_TEXTURE_2D, self._cube_covered_texture)
                    Buffer.isTextureExist(self.__program.uniformVariablesDict, 1)
                    Buffer.setTextureInfo(self.__program.uniformVariablesDict, 0)
                    for x_d, y_d, z_d in self.default_cube_position:
                        self.__translation_matrix[0][-1] = x_d
                        self.__translation_matrix[1][-1] = y_d
                        self.__translation_matrix[2][-1] = z_d
                        Buffer.drawFromVaoBuffer(self.__settings.get_scene_params('draw', 'type'),
                                                 self.__program.uniformVariablesDict, 
                                                 RotationMatrix=self.rotation_matrix,
                                                 ViewMatrix=self.__view_matrix,
                                                 ProjectionMatrix=self.__projection_matrix,
                                                 NormalMatrix=self.__normal_matrix,
                                                 TranslationMatrix=self.__translation_matrix,
                                                 texture=self._cube_covered_texture)
                    glBindTexture(GL_TEXTURE_2D, 0)
                # else:
                #     Buffer.isTextureExist(self.__program.uniformVariablesDict, 0)
                #     for atomIndex, (xD, yD, zD) in enumerate(self.__calculation['POSITIONS'][self._step]):
                #         if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex]:
                #             self.__translationMatrix[0][-1] = xD
                #             self.__translationMatrix[1][-1] = yD
                #             self.__translationMatrix[2][-1] = zD
                #             Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
                #         if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex] + '_Bond':
                #             self.__translationMatrix[0][-1] = xD
                #             self.__translationMatrix[1][-1] = yD
                #             self.__translationMatrix[2][-1] = zD
                #             Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
                Buffer.endOfDrawing()

    def mouseMoveEvent(self, event):
        # Get position relative to the widget
        self.mouse_x_position = event.x()
        self.mouse_y_position = event.y()
   
    def mousePressEvent(self, event):
        # Get position relative to the widget
        x = event.x()
        y = event.y()
        print(f"Mouse pressed at: ({x}, {y})")

    def keyPressEvent(self, event):
        key = event.key()
        print(f"Found key {key}")
        #if key == QtCore.Qt.Key_1:
        #    self.selected_bin = 1
        #    self.set_current_bin()

    def change_light(self, light_indx):
        self.__settings.set_scene_params(not self.__settings.get_scene_params('light', 'states', light_indx), 'states', light_indx)
        if self.__settings.get_scene_params('light', 'states', light_indx):
            glEnable(self.__settings.get_scene_params('light', 'variables', light_indx))
            glLight(self.__settings.get_scene_params('light', 'variables', light_indx), GL_POSITION, 
                    (*self.__settings.get_scene_params('light', 'default', light_indx), 1))
            glLightfv(self.__settings.get_scene_params('light', 'variables', light_indx), GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
            glLightfv(self.__settings.get_scene_params('light', 'variables', light_indx), GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
            glLightfv(self.__settings.get_scene_params('light', 'variables', light_indx), GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        else:
            glDisable(self.__settings.get_scene_params('light', 'variables', light_indx))

    def change_light_position(self, light_indx, new_position):
        self.__settings.set_scene_params(new_position, 'light', 'positions', light_indx)

    # def displayResize(self, event):
    #     self.__display = [int(event.w), int(event.h)]
    #     self.windowSize = [int(event.w), int(event.h)]
    #     difference = [int(self.__display[i] - self.__defaultDisplay[i]) for i in range(2)]
    #     if difference[0] > difference[1]:
    #         self.__display[1] = self.__defaultDisplay[1] + int(difference[0] * 3 / 4)
    #     elif difference[0] < difference[1]:
    #         self.__display[0] = self.__defaultDisplay[0] + int(difference[1] * 4 / 3)
    #     self.displayScaling = self.__display[0] / self.__defaultDisplay[0]

    #     nlw = (event.w - self.__display[0]) // 2
    #     nlh = (event.h - self.__display[1]) // 2

    #     self._displayCenter = [event.w // 2, event.h // 2]
    #     self.newCoordinateStart = [nlw, nlh]
    #     glViewport(nlw, nlh, self.__display[0], self.__display[1])

    def load_calculation_info(self, calculation):
        self.__calculation = calculation
        self.__is_calculation_loaded = True

    def complete_load_of_calculation(self):
        self.__primitives.clear()
        self._VBOBuffers.clear()
        self._buffers_labels.clear()
        self.__cell_position[1] = self.__calculation['BASIS_VERT'].max()
        radii = [1.0 , 1.15]
        for _, atom in enumerate(self.__calculation['ATOMSINFO']):
            for indx, selection_type in enumerate(['', '_Sel']):
                self.__primitives[atom + selection_type] = Primitives(1, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Sphere(self.__calculation['ATOMSINFO'][atom]['RADII'] * radii[indx], 32, 32)
                self._VBOBuffers.append(VRVBO(self.__primitives[atom + selection_type][:-1], self.__primitives[atom + selection_type][-1]).createVaoBuffer())
                self._buffers_labels.append(key)
        self.__is_calculation_loaded = False

    def without_calculation(self):
        self.__calculation = None
        self.__primitives.clear()
        self._VBOBuffers.clear()
        self._buffers_labels.clear()
        self.__cell_position[1] = 20
        self.__primitives = __default_primitives
        self._VBOBuffers.append(VRVBO(self.__primitives['Quad'][:-1], self.__primitives['Quad'][-1]).createVaoBuffer())

    def set_default_rotation_matrix(self):
        self.rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
                                         [0.0, 0.0, 1.0, 0],
                                         [0.0, -1.0, 0.0, 0.0],
                                         [self._x_d, self._y_d, self._z_d, self._scale_parameter]], dtype=np.float64)

    def cell_draw(self, cell, draw_cell=False, draw_axes=False, line_width=3):
        """Draw cell of model."""
        edges = ((0, 1), (0, 3), (0, 4), (2, 1), (2, 3), (2, 7), (6, 3), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7)) if not drawAxes else ((0, 1), (0, 4), (2, 1), (2, 7), (6, 4), (6, 7), (5, 1), (5, 4), (5, 7))
        glLineWidth(line_width)
        glBegin(GL_LINES)
        if draw_cell:
            for edge in edges:
                for vertex in edge:
                    glColor4f(1.0, 1.0, 0.0, 1.0)
                    glVertex3fv(cell[vertex])
        if draw_axes:
            for color, edge in [((1.0, 0.0, 0.0), (3, 6)), ((0.0, 1.0, 0.0), (3, 0)), ((0.0, 0.0, 1.0), (3, 2))]:
                glColor4f(*color, 1.0)
                glVertex3fv(cell[edge[0]])
                glVertex3fv(cell[edge[1]])
        glEnd()

    def load_texture(self):  # , texture
        image = Image.open(os.path.join(self.__project_directory, 'VR_icons', 'PROCHEM-logo.png'))
        image = image.convert("RGBA")

        img_data = image.tobytes()

        self._cube_covered_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._cube_covered_texture)
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

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        # print(glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE))
        glBindTexture(GL_TEXTURE_2D, 0)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def define_rotation_around_axes(x_d, y_d, z_d, scale_parameter, x_r, y_r, z_r, limit_rotations=True):
        if limit_rotations:
            x_r, y_r, z_r = x_r % 360 - 180, y_r % 360 - 180, z_r % 360 - 180
        x_rotation = np.array([[1.0, 0.0, 0.0, 0.0],
                               [0.0, np.cos(np.radians(x_r)), -np.sin(np.radians(x_r)), 0.0],
                               [0.0, np.sin(np.radians(x_r)), np.cos(np.radians(x_r)), 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        y_rotation = np.array([[np.cos(np.radians(y_r)), 0.0, np.sin(np.radians(y_r)), 0.0],
                               [0.0, 1.0, 0.0, 0.0],
                               [-np.sin(np.radians(y_r)), 0.0, np.cos(np.radians(y_r)), 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        z_rotation = np.array([[np.cos(np.radians(z_r)), -np.sin(np.radians(z_r)), 0.0, 0.0],
                               [np.sin(np.radians(z_r)), np.cos(np.radians(z_r)), 0.0, 0.0],
                               [0.0, 0.0, 1.0, 0.0],
                               [0.0, 0.0, 0.0, 1.0]], dtype=np.float64)
        matrix = np.dot(z_rotation, np.dot(y_rotation, x_rotation))
        matrix[3][0], matrix[3][1], matrix[3][2] = x_d, y_d, z_d
        matrix[3][3] = scale_parameter
        return matrix

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def define_rotation(define_rotation_function, rotation_matrix, rotation_info, x_d, y_d, z_d, scale_parameter):
        if rotation_info[0] or rotation_info[1] or x_d or y_d or z_d or scale_parameter - 1.0:
            rotation_matrix = np.dot(rotation_matrix, define_rotation_function(x_d, y_d, z_d, scale_parameter, rotation_info[1], 0, rotation_info[0]))
            # self.__lights = np.dot(np.asarray(self.__lightsDefault), self.rotationMatrix)
        return rotation_matrix

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def define_normal_matrix(view_matrix, rotation_matrix):
        model_view_matrix = np.dot(view_matrix, rotation_matrix.transpose())
        return np.linalg.inv(model_view_matrix).transpose()[:3,:3]

    def select_atom(self, select):
        self.back_step, self.forward_step = False, False
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
            self.addMessage('This atom was already chose.' if select else 'This atom was already deleted.', self.__class__.__name__)
        pygame.time.wait(200)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def nonoptimal_dimension_search(positions, number_of_dividings):
        length = len(positions) - 1
        size_array = np.zeros((3, number_of_dividings + 1))
        delta_dim = np.zeros(3)
        for iteration in range(number_of_dividings + 1):
            step = iteration * length // number_of_dividings
            pos = positions[step].transpose()
            size_array[0] = pos[0].max() - pos[0].min()
            size_array[1] = pos[1].max() - pos[1].min()
            size_array[2] = pos[2].max() - pos[2].min()
        size_array = np.asarray(sizeArray)
        for index in range(3):
            delta_dim[index] = size_array[index].max() - size_array[index].min()
        return delta_dim.argsort()[-2]

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search_body(num, index, positions, indexes, dimension, bond_length):
        highest_index = max_index = len(indexes) - num
        min_index = 0
        now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
        pos = positions[index][dimension]
        while True:
            index_comp = indexes[now_index - 1 + num]
            index_comp_next = indexes[now_index + num]
            statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
            statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
            if statement1 and not statement2:
                break
            elif now_index == highest_index - 1 and statement1 and statement2:
                now_index = highest_index
                break
            elif now_index == 0 and not statement1:
                break
            elif statement1 and statement2:
                min_index = now_index
                summary = now_index + max_index
                now_index = summary // 2 if not summary % 2 else summary // 2 + 1
            else:
                max_index = now_index
                summary = now_index + min_index
                now_index = summary // 2 if not summary % 2 else summary // 2 + 1
        tracking_pos = positions[index]
        returning_indexes = []
        for another_index in indexes[num + 1:now_index + num]:
            target_pos = positions[another_index]
            length = np.linalg.norm(tracking_pos - target_pos)
            if length <= bond_length:
                returning_indexes.append(another_index)
        return np.array(returning_indexes)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search(search_algorithm, positions, indexes, dimension, bond_length):
        neighbours = dict()
        indexes_cp = indexes[:-1]
        for num, index in enumerate(indexes_cp):
            neighbours[int(index)] = search_algorithm(num, index, positions, indexes, dimension, bond_length)
        return neighbours

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search_between_types_body(index, positions, indexes, dimension, bond_length):
        highest_index = max_index = len(indexes)
        min_index = 0
        now_index = max_index // 2 if not max_index % 2 else max_index // 2 + 1
        pos = positions[index][dimension]
        while True:
            index_comp = indexes[now_index - 1]
            index_comp_next = indexes[now_index]
            statement1 = abs(pos - positions[index_comp][dimension]) <= bond_length
            statement2 = abs(pos - positions[index_comp_next][dimension]) <= bond_length
            if statement1 and not statement2:
                break
            elif now_index == highest_index - 1 and statement1 and statement2:
                now_index = highest_index
                break
            elif now_index == 0 and not statement1:
                break
            elif statement1 and statement2:
                min_index = now_index
                summary = now_index + max_index
                now_index = summary // 2 if not summary % 2 else summary // 2 + 1
            else:
                max_index = now_index
                summary = now_index + min_index
                now_index = summary // 2
        tracking_pos = positions[index]
        returning_indexes = []
        for another_index in indexes[:now_index]:
            target_pos = positions[another_index]
            length = np.linalg.norm(tracking_pos - target_pos)
            if length <= bond_length:
                returning_indexes.append(another_index)
        return np.array(returning_indexes)

    @staticmethod
    @jit(fastmath=True, nopython=True, cache=True)
    def neighbours_search_between_types(search_algorithm, positions, indexes_type1, indexes_type2, dimension, bond_length):
        neighbours = dict()
        for _, index in enumerate(indexes_type1):
            neighbours[int64(index)] = search_algorithm(index, positions, indexes_type2, dimension, bond_length)
        return neighbours

    def calculate_bonds(self):  # необходимо отсортировать массив по x, y, z и смотреть начиная с какого то элемента массива расстояние. Если оно больше заданного, то не включаем в рассмотрение, если меньше, то включаем и при этом соответствующим образом сдвигаем далее индекс поиска
        one_step_positions = self.__calculation['POSITIONS'][self._step]
        biggest_dim = self.nonoptimal_dimension_search(self.__calculation['POSITIONS'], 9)
        if self._all_bonds_calculate:
            one_step_positions_tr = one_step_positions.transpose()
            indexes_big = one_step_positions_tr[biggest_dim].argsort()
            neighbours = self.neighbours_search(self.neighbours_search_body, one_step_positions, indexes_big, biggest_dim, self._bond_length)
        else:
            type1, type2 = 'Mo', 'S'
            indexes1, indexes2 = self.__calculation['ATOM-NUMBERS'][type1], self.__calculation['ATOM-NUMBERS'][type2]
            one_step_positions_type2 = one_step_positions[indexes2]
            one_step_positions_tr = one_step_positions_type2.transpose()
            indexes_big = one_step_positions_tr[biggest_dim].argsort() + min(indexes2)
            neighbours = self.neighbours_search_between_types(self.neighbours_search_between_types_body, one_step_positions, indexes1, indexes_big, biggest_dim, self._bond_length)

    def prepare_bond_buffers(self):
        atoms = self.__calculation['ATOMNAMES']
        if self._bond_radius is None and self._bond_length is None:
            for atom in set(atoms):
                self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._default_bond_radius, self._default_bond_length / 2, 32)
        else:
            for atom in set(atoms):
                self.__primitives[f'{atom}_Bond'] = Primitives(1.0, self.__calculation['ATOMSINFO'][atom]['COLORVALUE']).Tube(self._bond_radius[f'{atom}_Bond'], self._bond_length[f'{atom}_Bond'] / 2, 32)
        for key in set(atoms):
            self._VBOBuffers.append(VRVBO(self.__primitives[key + '_Bond'][:-1], self.__primitives[key + '_Bond'][-1]).createVaoBuffer())
            self._buffers_labels.append(key + '_Bond')

    # def run(self):
    #     targetFps = 60
    #     prevTime = time.time()
    #     print(self._VBOBuffers)
    #     run = True
    #     while run:
    #         if self.__isCalculationLoaded:
    #             self.completeLoadOfCalculation()
    #         # glLoadIdentity()
    #         # glMultMatrixf(self.rotationMatrix)
    #         if self.isPerspective:
    #             self.__projectionMatrix = self.__perspectiveMatrix
    #         else:
    #             self.__projectionMatrix = self.__orthographicMatrix
    #         if self._parentWindowClosed:
    #             break
    #         for event in pygame.event.get():
    #             if event.type == pygame.QUIT:
    #                 self.BackStep, self.ForwardStep = False, False
    #                 run = False
    #                 self.__app.closeAllWindows()
    #                 break
    #             if event.type == pygame.KEYDOWN:
    #                 if event.key == pygame.K_ESCAPE:
    #                     self.BackStep, self.ForwardStep = False, False
    #                     run = False
    #                     self.__app.closeAllWindows()
    #                     break
    #                 if event.key == pygame.K_F4:
    #                     raise KeyError("Pushed exit key. Don't push F4 if you don't want to exit program.")
    #             if event.type == pygame.MOUSEMOTION and event.type != pygame.WINDOWLEAVE:
    #                 coord_x, coord_y = pygame.mouse.get_pos()
    #                 coord_x_mouse, coord_y_mouse = pygame.mouse.get_rel()
    #                 if self.mousePressed:
    #                     self.BackStep, self.ForwardStep = False, False
    #                     if self.onlyKeyboardSelect:
    #                         pygame.mouse.set_visible(False)
    #                     self.rotationInfo[0] -= (event.rel[0]) * 0.4
    #                     self.rotationInfo[1] += (event.rel[1]) * 0.4
    #             if event.type == pygame.MOUSEBUTTONUP:
    #                 if self.onlyKeyboardSelect:
    #                     pygame.mouse.set_visible(True)
    #             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
    #                 self._scaleParameter = self._scaleParameter * 0.92
    #                 pygame.time.wait(10)
    #             if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
    #                 self._scaleParameter = self._scaleParameter * 1.08
    #                 pygame.time.wait(10)
    #             if event.type == pygame.MOUSEBUTTONDOWN and self._BuffersLabels:
    #                 if event.button == 1:
    #                     if not self.onlyKeyboardSelect:
    #                         self.selectAtom(True)
    #                 if event.button == 3:
    #                     if not self.onlyKeyboardSelect:
    #                         self.selectAtom(False)

    #             if event.type == pygame.VIDEORESIZE:
    #                 self.displayResize(event)

    #         keypress = pygame.key.get_pressed()

    #         # Отдаление модели при нажатии клавиши - на кейпаде
    #         if keypress[pygame.K_KP_MINUS] or keypress[pygame.K_MINUS]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self._scaleParameter = self._scaleParameter * 1.03
    #             pygame.time.wait(10)
    #         # Приближение модели при нажатии кнопки + на кейпаде
    #         if keypress[pygame.K_KP_PLUS] or keypress[pygame.K_EQUALS]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self._scaleParameter = self._scaleParameter * 0.97
    #             pygame.time.wait(10)
    #         ##################################
    #         if keypress[pygame.K_BACKSPACE]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[0], self.rotationInfo[1] = 0.0, 0.0
    #             self._xD, self._yD, self._zD = 0, 0, 0
    #             self._scaleParameter = 1.0
    #             self.setDefaultRotationMatrix()
    #             self.__lights = np.dot(np.asarray(self.__lightsDefault), self.rotationMatrix)

    #         if keypress[pygame.K_LEFT]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[0] -= 1.5
    #         if keypress[pygame.K_RIGHT]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[0] += 1.5
    #         if keypress[pygame.K_UP]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[1] += 1.5
    #         if keypress[pygame.K_DOWN]:
    #             self.BackStep, self.ForwardStep = False, False
    #             self.rotationInfo[1] -= 1.5
    #         if keypress[pygame.K_z]:
    #             self._xD = self._xD - 0.1
    #         if keypress[pygame.K_x]:
    #             self._xD = self._xD + 0.1
    #         if keypress[pygame.K_j]:
    #             self._zD = self._zD + 0.1
    #         if keypress[pygame.K_u]:
    #             self._zD = self._zD - 0.1
    #         if keypress[pygame.K_i]:
    #             self._fogPower += 1
    #             time.sleep(0.08)
    #         if keypress[pygame.K_k]:
    #             if self._fogPower > 1:
    #                 self._fogPower -= 1
    #                 time.sleep(0.08)
    #         if keypress[pygame.K_o]:
    #             self._fogDensity = self._fogDensity * 1.05
    #             time.sleep(0.08)
    #         if keypress[pygame.K_l]:
    #             self._fogDensity = self._fogDensity / 1.05
    #             time.sleep(0.08)
    #         if keypress[pygame.K_s]:
    #             for ind, name in enumerate(self.__calculation['ATOMNAMES']):
    #                 if name.split('_')[-1] != 'Sel':
    #                     self.__calculation['ATOMNAMES'][ind] += '_Sel'

    #         if (keypress[pygame.K_COMMA] or self.BackStep) and self._BuffersLabels:
    #             self._step -= 1 * self._speed
    #             if self._step < 0:
    #                 self._step = self.__calculation['STEPS'] - 1 + self._step
    #             self.__visualWindow.StepSlider.setSliderPosition(self._step)
    #             self.BackStep = True
    #         if (keypress[pygame.K_PERIOD] or self.ForwardStep) and self._BuffersLabels:
    #             self._step += 1 * self._speed
    #             if self._step >= self.__calculation['STEPS']:
    #                 self._step = self._step - self.__calculation['STEPS']
    #             self.__visualWindow.StepSlider.setSliderPosition(self._step)
    #             self.ForwardStep = True

    #         if keypress[pygame.K_a]:
    #             self.selectAtom(True)
    #         if keypress[pygame.K_d]:
    #             self.selectAtom(False)

    #         if keypress[pygame.K_p]:
    #             self.__visualWindow.processingStart()

    #         # Движение модели мышкой
    #         for _ in pygame.mouse.get_pressed():
    #             if pygame.mouse.get_pressed()[0] == 1:
    #                 self.mousePressed = True
    #             elif pygame.mouse.get_pressed()[0] == 0:
    #                 self.mousePressed = False

    #         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    #         glClearColor(*self._backgroundColor)
    #         self.rotationMatrix = self.defineRotation(self.defineRotationAroundAxes, self.rotationMatrix, self.rotationInfo, self._xD, self._yD, self._zD, self._scaleParameter)
    #         self.normalMatrix = self.defineNormalMatrix(self.__viewMatrix, self.rotationMatrix)
    #         # # Отрисовка границ ячейки
    #         # if self.drawCell and self._BuffersLabels:
    #         #     self.cellDraw(self.__calculation['BASIS_VERT'], self.drawCell, self.drawAxes, 3)

    #         # x, y, z = self.findWindowDimensions(-5)
    #         for index, Buffer in enumerate(self._VBOBuffers):
    #             Buffer.prepareToDraw(self.__program.program)
    #             Buffer.setLightSettings(self.__program.uniformVariablesDict, self.__Ka, self.__Kd, self.__Ks, self.__Shininess, self.__lights, self.__intensities)
    #             Buffer.setFogParameters(self.__program.uniformVariablesDict, self.__cellPosition, self._fogColor, self._fogMinDist, self._fogMaxDist, self._fogPower, self._fogDensity)
    #             if not self._BuffersLabels:
    #                 glActiveTexture(GL_TEXTURE0)
    #                 glBindTexture(GL_TEXTURE_2D, self._cubeCoveredTexture)
    #                 Buffer.isTextureExist(self.__program.uniformVariablesDict, 1)
    #                 Buffer.setTextureInfo(self.__program.uniformVariablesDict, 0)
    #                 for xD, yD, zD in self.defaultCubePosition:
    #                     self.__translationMatrix[0][-1] = xD
    #                     self.__translationMatrix[1][-1] = yD
    #                     self.__translationMatrix[2][-1] = zD
    #                     Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
    #                 glBindTexture(GL_TEXTURE_2D, 0)
    #             else:
    #                 Buffer.isTextureExist(self.__program.uniformVariablesDict, 0)
    #                 for atomIndex, (xD, yD, zD) in enumerate(self.__calculation['POSITIONS'][self._step]):
    #                     if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex]:
    #                         self.__translationMatrix[0][-1] = xD
    #                         self.__translationMatrix[1][-1] = yD
    #                         self.__translationMatrix[2][-1] = zD
    #                         Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
    #                     if self._BuffersLabels[index] == self.__calculation['ATOMNAMES'][atomIndex] + '_Bond':
    #                         self.__translationMatrix[0][-1] = xD
    #                         self.__translationMatrix[1][-1] = yD
    #                         self.__translationMatrix[2][-1] = zD
    #                         Buffer.drawFromVaoBuffer(self.__drawType, self.__program.uniformVariablesDict, self.rotationMatrix.transpose(), self.__viewMatrix, self.__projectionMatrix.transpose(), self.normalMatrix, self.__translationMatrix)
    #             Buffer.endOfDrawing()
    #         pygame.display.flip()
    #         self.rotationInfo[0], self.rotationInfo[1] = 0.0, 0.0
    #         self._scaleParameter = 1.0
    #         self._xD, self._yD, self._zD = 0.0, 0.0, 0.0
    #         currTime = time.time()
    #         diff = currTime - prevTime
    #         delay = max(1.0 / targetFps - diff, 0)
    #         time.sleep(delay)
    #         fps = 1.0 / (delay + diff)
    #         prevTime = currTime
    #     for _ in range(len(self._VBOBuffers)):
    #         self._VBOBuffers.pop(0).__del__()
    #     self.__visualWindow.close()
    #     pygame.quit()
