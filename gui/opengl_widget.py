from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QImage, QSurfaceFormat, QOpenGLContext
from PySide6.QtCore import QTimer, Qt
from visual.shaders.shaders import Shaders
from visual.camera import Camera
from visual.light import SceneLight
from visual.primitives import Primitive
from visual.axes import Axes
from visual.cell import Cell
from visual.jit_functions.visual import *
from visual.jit_functions.primitives import *
import numpy as np
from PIL import Image, ImageQt
import gui.resource_rc
import logging
import random
import os
import OpenGL
from OpenGL.GL import *

OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)


class GLWidget(QOpenGLWidget):
    # __default_primitives = {'Quad': Primitive(*Quad(5, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)])),
    #                         'Sphere': Primitive(*Sphere(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)], 32, 32)),
    #                         'Torus': Primitive(*Torus(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)], 0.5, 1, 32, 32)),
    #                         'Cube': Primitive(*Cube(1, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]))}
    def __init__(self, parent=None, settings=None, project_directory=None):
        super().__init__(parent)
        self.set_minimal_supported_format() # TODO check how to set once minimal supported format and create context
        context = QOpenGLContext()
        context.create()

        self.__settings = settings
        self.__project_directory = project_directory
        self.__program = None
        self.__camera = Camera(self.__settings)
        self.__camera.set_perspective_matrix(self.width(), self.height())
        self.__light = SceneLight(self.__settings)
        self.__default_primitive = None # self.__default_primitives['Quad']
        self.__axes = None
        self.__cell = None
        self.__texture = {}

        self.__dx, self.__dy, self.__dz, self.__scale = 0.0, 0.0, 0.0, 1.0
        self.__mouse_x_pos, self.__mouse_y_pos = 0, 0
        self.__trace_mouse = False
        self.__mouse_dx, self.__mouse_dy = 0, 0
        self.__rotation_angle = [0, 0, 0]
        
        self.__rotation_matrix = np.identity(4, dtype=np.float32)
        # self.__rotation_matrix = np.array([[-1.0, 0.0, 0.0, 0.0],
        #                                    [0.0, 0.0, 1.0, 0],
        #                                    [0.0, -1.0, 0.0, 0.0],
        #                                    [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)

        self.__timer = QTimer()
        self.__timer.timeout.connect(self.update)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glLineWidth(3.0)
        self.__program = Shaders(os.path.join(self.__project_directory, 'visual', 'shaders'), [r'vertex.glsl', r'fragment.glsl'], ['VERTEX', 'FRAGMENT'])
        self.load_texture(":/icons/logo/PROCHEM-logo.png")
        self.__default_primitive = Primitive(*Quad(5, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)]))
        self.__default_primitive.set_texture(self.__texture['default'])
        self.__sphere = Primitive(*Sphere(0.3, [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0)], 32, 32))
        self.__axes = Axes(self.__settings)
        self.__cell = Cell([0.0, 2.733673, 2.733673], [2.733673, 0.0, 2.733673], [2.733673, 2.733673, 0.0], self.__settings)
        self.__timer.start(16)

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        self.__camera.set_perspective_matrix(w, h)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(*self.__settings.get_scene_params('background', 'color'))
        if self.__program:
            glUseProgram(self.__program.program)
            glUniformMatrix4fv(self.__program.uniform_variables[('Rotation', 'mat4')], 1, GL_TRUE, self.__rotation_matrix)
            self.__camera.send_info_to_shader(self.__program.uniform_variables)
            self.__light.send_light_info(self.__program.uniform_variables)
            # self.__default_primitive.draw(self.__program.uniform_variables)
            for x_i in range(-1, 0):
                for y_i in range(0, 1):
                    for z_i in range(0, 1):
                        self.__sphere.translate(x_i * 1, y_i * 1, z_i * 1)
                        self.__sphere.draw(self.__program.uniform_variables)
            if self.__trace_mouse:
                self.__axes.draw(self.__program.uniform_variables)
            self.__cell.draw(self.__program.uniform_variables)
            glUseProgram(0)
                # Buffer.setFogParameters(self.__program.uniformVariablesDict, 
                #                         self.__settings.get_scene_params('view', 'eye_position'),
                #                         self.__settings.get_scene_params('fog', 'color'),
                #                         self.__settings.get_scene_params('fog', 'min_dist'),
                #                         self.__settings.get_scene_params('fog', 'max_dist'),
                #                         self.__settings.get_scene_params('fog', 'power'),
                #                         self.__settings.get_scene_params('fog', 'density'))
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

    def keyPressEvent(self, event):
        key = event.key()
        match key:
            case Qt.Key_Up:
                self.__rotation_angle = [-2, 0, 0]
                self.rotate(*self.__rotation_angle)
            case Qt.Key_Down:
                self.__rotation_angle = [2, 0, 0]
                self.rotate(*self.__rotation_angle)
            case Qt.Key_Left:
                self.__rotation_angle = [0, -2, 0]
                self.rotate(*self.__rotation_angle)
            case Qt.Key_Right:
                self.__rotation_angle = [0, 2, 0]
                self.rotate(*self.__rotation_angle)
            case Qt.Key_Q:
                self.__rotation_angle = [0, 0, 2]
                self.rotate(*self.__rotation_angle)
            case Qt.Key_E:
                self.__rotation_angle = [0, 0, -2]
                self.rotate(*self.__rotation_angle)
            case Qt.Key_Backspace:
                self.__rotation_angle = [0, 0, 0]
                self.__dx, self.__dy, self.__dz = 0.0, 0.0, 0.0
                self.__scale = 1.0
                self.__rotation_matrix = np.identity(4, dtype=np.float32)
            case Qt.Key_Plus:
                self.__scale += 0.1
            case Qt.Key_Minus:
                self.__scale -= 0.1
            case Qt.Key_J:
                self.__dy -= 0.1
            case Qt.Key_K:
                self.__dy += 0.1
            case Qt.Key_L:
                self.__dx += 0.1
            case Qt.Key_H:
                self.__dx -= 0.1
            case Qt.Key_N:
                self.__dz += 0.1
            case Qt.Key_M:
                self.__dz -= 0.1

    def mouseMoveEvent(self, event):
        if self.__trace_mouse:
            self.__mouse_dx = event.x() - self.__mouse_x_pos
            self.__mouse_dy = event.y() - self.__mouse_y_pos
           
            self.__rotation_angle = [self.__mouse_dy * 0.2, self.__mouse_dx * 0.2, 0]
            self.rotate(*self.__rotation_angle)

            self.__mouse_x_pos = event.x()
            self.__mouse_y_pos = event.y()
   
    def mousePressEvent(self, event):
        # Get position relative to the widget
        self.__mouse_x_pos = event.x()
        self.__mouse_y_pos = event.y()
        self.__trace_mouse = True

    def mouseReleaseEvent(self, event):
        self.__trace_mouse = False

    def rotate(self, dx, dy, dz):  # TODO rotation_info[1], 0, rotation_info[0]
        self.__rotation_matrix = rotate(self.__rotation_matrix, dx, dy, dz)

    def set_view_matrix(self):
        self.__camera.set_view_matrix()

    def set_perspective_matrix(self):
        self.__camera.set_perspective_matrix()

    def set_orthographic_matrix(self):
        self.__camera.set_orthographic_matrix()

    def set_projection_matrix(self):
        self.__camera.set_projection_matrix()

    def set_program(self, program):
        self.__program = program

    def set_settings(self, settings):
        self.__settings = settings

    def load_texture(self, image, is_qtype=True, texture_name="default"):
        img = None
        if is_qtype:
            img = QImage(image) # ":/icons/logo/PROCHEM-logo.png"
            img = ImageQt.fromqimage(img)
        else:
            img = Image.open(image) # os.path.join(self.__project_directory, "icons", "logo", "PROCHEM-logo.png")
        img = img.convert("RGBA")

        self.__texture[texture_name] = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.__texture[texture_name])

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1.0, 1.0, 1.0, 1.0])

        glTexParameteri(
            GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR
        )  # position 3 possible parameters: GL_NEAREST, GL_LINEAR
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            img.width,
            img.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img.tobytes(),
        )
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

    def set_minimal_supported_format(self):
        format = QSurfaceFormat()
        format.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
        format.setVersion(4, 3)  # Request OpenGL 4.3
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        format.setDepthBufferSize(24)
        QSurfaceFormat.setDefaultFormat(format)
