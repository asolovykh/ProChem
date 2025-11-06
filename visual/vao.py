"""Vertex array object class."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import numpy as np
import logging
import OpenGL
from OpenGL.GL import *
from OpenGL.arrays import vbo
from typing import Optional

OpenGL.ERROR_CHECKING = False
logger = logging.getLogger(__name__)

__all__ = ["VAO"]


class VAO:
    """Forms vertex buffer object from inputted arrays and creates vertex array object."""
    def __init__(self, array_elements: tuple[np.ndarray, ...], indexes: np.ndarray, usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER'):  # GL_DYNAMIC_DRAW
        """Initializes VBO arrays of indexes and vertices, colors, normals, texCords."""
        self.vao = None
        self.array = np.array([])
        self.array_elements = tuple()
        self.element_size = 0
        self.elements_number = 0
        for index, element in enumerate(array_elements):
            if index == 0:
                element = element.astype(np.float32)
                self.elements_number = element.shape[0]
                self.array_elements = (element.shape[1], )
                self.element_size = element.itemsize
                self.array = element
            else:
                element = element.astype(np.float32)
                self.array_elements = self.array_elements + (element.shape[1], )
                self.array = np.concatenate((self.array, element), axis=1)
        self.dimension_size = sum(self.array_elements)
        self.array = vbo.VBO(self.array, usage, target)
        
        indexes = indexes.astype(np.uint32)
        self.indexes = vbo.VBO(indexes, usage, GL_ELEMENT_ARRAY_BUFFER)

    def __del__(self) -> None:
        """A rule for deleting a VAO object."""
        if glDeleteBuffers:
            self.array.delete()
            # if self.vao is not None and glDeleteVertexArrays:
            #     glDeleteVertexArrays(1, [self.vao])
            if self.indexes is not None:
                self.indexes.delete()

    def create(self) -> None:
        """Creates VAO buffer from VBO buffers and return the class object."""
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.array.bind()
        for index, size in enumerate(self.array_elements):
            glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, self.dimension_size * self.element_size, self.array + (sum(self.array_elements[:index + 1]) - self.array_elements[index]) * self.element_size)  # ctypes.c_void_p(0)
            glEnableVertexAttribArray(index)
        self.array.unbind()
        glBindVertexArray(0)
        return self

    def get_indexes(self) -> Optional[vbo.VBO]:
        """Returns VBO indexes."""
        return self.indexes

    def load_uniform_vec4(self, location, vec4) -> None:
        """Loading of vec4f uniform variable into program."""
        glUniform4f(location, *vec4)

    def load_uniform_vec3(self, location, vec3) -> None:
        """Loading of vec3f uniform variable into program."""
        glUniform3f(location, *vec3)

    def load_uniform_mat4(self, location, mat4) -> None:
        """Loading of mat4fv uniform variable into program."""
        glUniformMatrix4fv(location, 1, GL_TRUE, mat4)
        # glUniformMatrix4fv(location, 1, GL_FALSE, glm.value_ptr(mat4)) # <- set GL_TRUE to transform matrix before sending it to shader

    def load_uniform_mat3(self, location, mat3) -> None:
        """Loading of mat3fv uniform variable into program."""
        glUniformMatrix4fv(location, 1, GL_TRUE, mat3)
        # glUniformMatrix3fv(location, 1, GL_FALSE, glm.value_ptr(mat3))

    def load_uniform_float(self, location, uFloat) -> None:
        """Loading of float uniform variable into program."""
        glUniform1f(location, uFloat)

    def load_uniform_int(self, location, uInt) -> None:
        """Loading of int uniform variable into program."""
        glUniform1i(location, uInt)

    def defineUniformVariableType(self, varType) -> None:
        """Automatically define type of uniform variable."""
        if varType == 'vec4':
            return self.load_uniform_vec4
        elif varType == 'vec3':
            return self.load_uniform_vec3
        elif varType == 'mat3':
            return self.load_uniform_mat3
        elif varType == 'mat4':
            return self.load_uniform_mat4
        elif varType == 'float':
            return self.load_uniform_float
        else:
            raise VAOError('Undefined shader variable type.')

    def prepareToDraw(self, program) -> None:
        """Starts to use the pointed program and binds VAO buffer."""
        glUseProgram(program)

    def endOfDrawing(self) -> None:
        """Unbinds VAO buffer and ends to use the pointed program."""
        glUseProgram(0)

    def setFogParameters(self, uniform_variables, eyePosition, fogColor, fogMinDist, fogMaxDist, fogPower, fogDensity) -> None:
        """Loads fog settings into program."""
        self.load_uniform_vec3(uniform_variables[('EyePosition', 'vec3')], eyePosition)
        self.load_uniform_vec4(uniform_variables[('fog.FogColor', '=')], fogColor)
        # self.load_uniform_float(uniform_variables[('fog.FogMaxDist', '1')], fogMaxDist)
        # self.load_uniform_float(uniform_variables[('fog.FogMinDist', '1')], fogMinDist)
        self.load_uniform_int(uniform_variables[('fog.FogPower', '1')], fogPower)
        self.load_uniform_float(uniform_variables[('fog.FogDensity', '1')], fogDensity)

    def isTextureExist(self, uniform_variables, value):
        self.load_uniform_int(uniform_variables[('isTextureExist', 'int')], value)

    def setTextureInfo(self, uniform_variables, texture):
        self.load_uniform_int(uniform_variables[('textureMap', 'sampler2D')], texture)

    def drawFromVaoBuffer(self, primitiveType, uniform_variables, RotationMatrix='', ViewMatrix='', ProjectionMatrix='', TranslationMatrix='', texture='') -> None:
        """Sends command to draw elements from VAO buffer."""
        self.load_uniform_mat4(uniform_variables[('Rotation', 'mat4')], RotationMatrix)
        self.load_uniform_mat4(uniform_variables[('Translation', 'mat4')], TranslationMatrix)
        self.load_uniform_mat4(uniform_variables[('View', 'mat4')], ViewMatrix)
        self.load_uniform_mat4(uniform_variables[('Projection', 'mat4')], ProjectionMatrix)
        #self.load_uniform_mat3(uniform_variables[('NormalMatrix', 'mat3')], NormalMatrix)
        if self.indexes is not None:
            self.indexes.bind()
        if texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)
        glDrawElements(primitiveType, self.elements_number, GL_UNSIGNED_INT, None)
        if texture:
            glBindTexture(GL_TEXTURE_2D, 0)
        if self.indexes is not None:
            self.indexes.unbind()


class VAOError(Exception):
    """Class for processing of errors in VAO class."""
    def __init__(self, message):
        """Initializing function."""
        super(VAOError, self).__init__(f'VAO error: {message}')
