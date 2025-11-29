from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtGui import QImage, QSurfaceFormat, QOpenGLContext
from PySide6.QtCore import QTimer, Qt
from visual.shaders.shaders import Shaders
from visual.scene import Scene
import logging
import os
import OpenGL
from OpenGL.GL import *

OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)


class GLWidget(QOpenGLWidget):
    def __init__(self, parent=None, settings=None, project_directory=None):
        super().__init__(parent)
        self.set_minimal_supported_format() # TODO check how to set once minimal supported format and create context
        context = QOpenGLContext()
        context.create()

        self.__settings = settings
        self.__project_directory = project_directory
        self.__program = None
        self.__scene = None

        self.__mouse_x_pos, self.__mouse_y_pos = 0, 0
        self.__trace_mouse = False
        self.__mouse_dx, self.__mouse_dy = 0, 0
        
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
        self.__settings.set_scene_params(self.width() / self.height(), 'view', 'perspective', 'aspect')
        self.__program = Shaders(os.path.join(self.__project_directory, 'visual', 'shaders'), [r'vertex.glsl', r'fragment.glsl'], ['VERTEX', 'FRAGMENT'])
        self.__scene = Scene(self.__settings)
        self.__scene.load_texture(":/icons/logo/PROCHEM-logo.png")
        # self.__scene.set_draw_buffer({'Sphere': {((0.2, 0, 0.5), 1.0): [[0, 0, 0], [1, 1, 1], [2, 2, 2]]}})
        self.__timer.start(16)

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, w, h)
        self.__settings.set_scene_params(w / h, 'view', 'perspective', 'aspect')
        if self.__scene is not None:
            self.__scene.update_camera()

    def paintGL(self):
        if self.__program:
            glUseProgram(self.__program.program)
            self.__scene.draw(self.__program, self.__trace_mouse)
            glUseProgram(0)

    def keyPressEvent(self, event):
        key = event.key()
        match key:
            case Qt.Key_Up:
                self.__scene.rotate(-2, 0, 0)
            case Qt.Key_Down:
                self.__scene.rotate(2, 0, 0)
            case Qt.Key_Left:
                self.__scene.rotate(0, -2, 0)
            case Qt.Key_Right:
                self.__scene.rotate(0, 2, 0)
            case Qt.Key_Q:
                self.__scene.rotate(0, 0, 2)
            case Qt.Key_E:
                self.__scene.rotate(0, 0, -2)
            case Qt.Key_Backspace:
                self.__scene.reset_scene_matrices()
            case Qt.Key_Equal:
                self.__scene.scale(1.02)
            case Qt.Key_Minus:
                self.__scene.scale(0.98)
            case Qt.Key_J:
                self.__scene.move_y(-0.1)
            case Qt.Key_K:
                self.__scene.move_y(0.1)
            case Qt.Key_L:
                self.__scene.move_x(0.1)
            case Qt.Key_H:
                self.__scene.move_x(-0.1)
            case Qt.Key_N:
                self.__scene.move_z(0.1)
            case Qt.Key_M:
                self.__scene.move_z(-0.1)
        self.parent().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        if self.__trace_mouse:
            self.__mouse_dx = event.x() - self.__mouse_x_pos
            self.__mouse_dy = event.y() - self.__mouse_y_pos
           
            self.__scene.rotate(self.__mouse_dy * 0.2, self.__mouse_dx * 0.2, 0)

            self.__mouse_x_pos = event.x()
            self.__mouse_y_pos = event.y()
   
    def mousePressEvent(self, event):
        self.__mouse_x_pos = event.x()
        self.__mouse_y_pos = event.y()
        self.__trace_mouse = True

    def mouseReleaseEvent(self, event):
        self.__trace_mouse = False

    def set_program(self, program):
        self.__program = program

    def set_settings(self, settings):
        self.__settings = settings

    def set_minimal_supported_format(self):
        format = QSurfaceFormat()
        format.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
        format.setVersion(4, 3)  # Request OpenGL 4.3
        format.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        format.setDepthBufferSize(24)
        QSurfaceFormat.setDefaultFormat(format)
