from PySide6.QtWidgets import QApplication, QMainWindow, QOpenGLWidget
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL import GL as gl


class GLWidget(QOpenGLWidget):
    """A custom QOpenGLWidget that draws a solid color."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PySide6 QOpenGLWidget Example")
        self.resize(600, 400)

    def initializeGL(self):
        """
        Called once before the first call to paintGL().
        Use this to set up OpenGL state, but not to issue drawing commands.
        """
        # Set the clear color to a solid gray
        gl.glClearColor(0.5, 0.5, 0.5, 1.0)

    def paintGL(self):
        """
        Called whenever the widget needs to be repainted.
        All OpenGL drawing commands should go here.
        """
        # Clear the color buffer with the background color set in initializeGL()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def resizeGL(self, w: int, h: int):
        """
        Called whenever the widget is resized.
        You can use this to update the viewport and projection matrix.
        """
        # Set the viewport to cover the entire widget area
