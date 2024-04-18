import numpy as np
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
from OpenGL.arrays import vbo


class VRVBO:
    """Forms vertex buffer object from inputted arrays."""
    def __init__(self, arrayElements: tuple[np.ndarray, ...], indexes: np.ndarray = None, usage='GL_STATIC_DRAW', target='GL_ARRAY_BUFFER'):  # GL_DYNAMIC_DRAW
        """Initializes VBO arrays of indexes and vertices, colors, normals, texCords."""
        self.vao = None
        self.array = np.array([])
        self.arrayElements = tuple()
        self.elementSize = 0
        self.elementsNumber = 0
        for index, element in enumerate(arrayElements):
            if index == 0:
                element = element.astype(np.float32)
                self.elementsNumber = element.shape[0]
                self.arrayElements = (element.shape[1], )
                self.elementSize = element.itemsize
                self.array = element
            else:
                element = element.astype(np.float32)
                self.arrayElements = self.arrayElements + (element.shape[1], )
                self.array = np.concatenate((self.array, element), axis=1)
        self.dimensionSize = sum(self.arrayElements)
        self.array = vbo.VBO(self.array, usage, target)
        self.indexes = None
        if indexes is not None:
            self.elementsNumber = len(indexes)
            self.indexes = vbo.VBO(indexes, usage, GL_ELEMENT_ARRAY_BUFFER)

    def __del__(self) -> None:
        """A rule for deleting a VRVBO object."""
        if glDeleteBuffers:
            self.array.delete()
            # if self.vao is not None and glDeleteVertexArrays:
            #     glDeleteVertexArrays(1, [self.vao])
            if self.indexes is not None:
                self.indexes.delete()

    def createVaoBuffer(self):
        """Creates VAO buffer from VBO buffers and return the class object."""
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.array.bind()
        for index, size in enumerate(self.arrayElements):
            glVertexAttribPointer(index, size, GL_FLOAT, GL_FALSE, self.dimensionSize * self.elementSize, self.array + (sum(self.arrayElements[:index + 1]) - self.arrayElements[index]) * self.elementSize)  # ctypes.c_void_p(0)
            glEnableVertexAttribArray(index)
        self.array.unbind()
        glBindVertexArray(0)
        return self

    def loadUniformVec4(self, location, vec4) -> None:
        """Loading of vec4f uniform variable into program."""
        glUniform4f(location, *vec4)

    def loadUniformVec3(self, location, vec3) -> None:
        """Loading of vec3f uniform variable into program."""
        glUniform3f(location, *vec3)

    def loadUniformMat4(self, location, mat4) -> None:
        """Loading of mat4fv uniform variable into program."""
        glUniformMatrix4fv(location, 1, GL_TRUE, mat4)

    def loadUniformMat3(self, location, mat3) -> None:
        """Loading of mat3fv uniform variable into program."""
        glUniformMatrix3fv(location, 1, GL_TRUE, mat3)

    def loadUniformFloat(self, location, uFloat) -> None:
        """Loading of float uniform variable into program."""
        glUniform1f(location, uFloat)

    def loadUniformInt(self, location, uInt) -> None:
        """Loading of int uniform variable into program."""
        glUniform1i(location, uInt)

    def defineUniformVariableType(self, varType):
        """Automatically define type of uniform variable."""
        if varType == 'vec4':
            return self.loadUniformVec4
        elif varType == 'vec3':
            return self.loadUniformVec3
        elif varType == 'mat3':
            return self.loadUniformMat3
        elif varType == 'mat4':
            return self.loadUniformMat4
        elif varType == 'float':
            return self.loadUniformFloat
        else:
            raise VRVBOError('Undefined shader variable type.')

    def prepareToDraw(self, program) -> None:
        """Starts to use the pointed program and binds VAO buffer."""
        glUseProgram(program)
        glBindVertexArray(self.vao)

    def endOfDrawing(self) -> None:
        """Unbinds VAO buffer and ends to use the pointed program."""
        glBindVertexArray(0)
        glUseProgram(0)

    def setLightSettings(self, uniformVariablesDict, Ka, Kd, Ks, Shininess, lightPositions, lightIntensities) -> None:
        """Loads light settings into program."""
        for index, position in enumerate(lightPositions):
            self.loadUniformVec4(uniformVariablesDict[(f'lights[{index}].Position', '')], position)
            self.loadUniformVec3(uniformVariablesDict[(f'lights[{index}].Intensity', '')], lightIntensities[index])
        self.loadUniformVec3(uniformVariablesDict[('Kd', 'vec3')], Kd)
        self.loadUniformVec3(uniformVariablesDict[('Ka', 'vec3')], Ka)
        self.loadUniformVec3(uniformVariablesDict[('Ks', 'vec3')], Ks)
        self.loadUniformFloat(uniformVariablesDict[('Shininess', 'float')], Shininess)

    def setFogParameters(self, uniformVariablesDict, eyePosition, fogColor, fogMinDist, fogMaxDist, fogPower, fogDensity) -> None:
        """Loads fog settings into program."""
        self.loadUniformVec3(uniformVariablesDict[('EyePosition', 'vec3')], eyePosition)
        self.loadUniformVec4(uniformVariablesDict[('fog.FogColor', '=')], fogColor)
        # self.loadUniformFloat(uniformVariablesDict[('fog.FogMaxDist', '1')], fogMaxDist)
        # self.loadUniformFloat(uniformVariablesDict[('fog.FogMinDist', '1')], fogMinDist)
        self.loadUniformInt(uniformVariablesDict[('fog.FogPower', '1')], fogPower)
        self.loadUniformFloat(uniformVariablesDict[('fog.FogDensity', '1')], fogDensity)

    def isTextureExist(self, uniformVariablesDict, value):
        self.loadUniformInt(uniformVariablesDict[('isTextureExist', 'int')], value)

    def setTextureInfo(self, uniformVariablesDict, texture):
        self.loadUniformInt(uniformVariablesDict[('textureMap', 'sampler2D')], texture)

    def drawFromVaoBuffer(self, primitiveType, uniformVariablesDict, ModelMatrix='', ViewMatrix='', ProjectionMatrix='', NormalMatrix='', TranslationMatrix='', texture='') -> None:
        """Sends command to draw elements from VAO buffer."""
        self.loadUniformMat4(uniformVariablesDict[('ModelMatrix', 'mat4')], ModelMatrix)
        self.loadUniformMat4(uniformVariablesDict[('ViewMatrix', 'mat4')], ViewMatrix)
        self.loadUniformMat4(uniformVariablesDict[('ProjectionMatrix', 'mat4')], ProjectionMatrix)
        self.loadUniformMat3(uniformVariablesDict[('NormalMatrix', 'mat3')], NormalMatrix)
        self.loadUniformMat4(uniformVariablesDict[('TranslationMatrix', 'mat4')], TranslationMatrix)
        if self.indexes is not None:
            self.indexes.bind()
        if texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture)
        glDrawElements(primitiveType, self.elementsNumber, GL_UNSIGNED_INT, None)
        if texture:
            glBindTexture(GL_TEXTURE_2D, 0)
        if self.indexes is not None:
            self.indexes.unbind()


class VRVBOError(Exception):
    """Class for processing of errors in VRVBO class."""
    def __init__(self, message):
        """Initializing function."""
        super(VRVBOError, self).__init__(f'VRVBO error: {message}')