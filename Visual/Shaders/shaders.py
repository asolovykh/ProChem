import traceback
import os
import logging
import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *
logger = logging.getLogger(__name__)


class VRShaders:
    """VaspReader shaders compile class. Union shader files into programs for next using in VaspReader visualisation
    functions."""
    VERTEX = GL_VERTEX_SHADER
    FRAGMENT = GL_FRAGMENT_SHADER
    GEOMETRY = GL_GEOMETRY_SHADER
    TESS_CONTROL = GL_TESS_CONTROL_SHADER
    TESS_EVALUATION = GL_TESS_EVALUATION_SHADER
    COMPUTE = GL_COMPUTE_SHADER

    def __init__(self, directory: str, shaderFiles: list[str], shaderTypes: list[str]):
        """Initialize class function. Requires:

        directory - directory of shader files,

        shaderFiles - list of string names of shaders for next form pathnames of files,

        shaderTypes - shaders type: VERTEX, FRAGMENT, GEOMETRY, TESS_CONTROL, TESS_EVALUATION or COMPUTE.

        Please always check positions of files and types of shaders in list."""
        self.program = 0
        self.shaders = dict()
        self.uniformVariablesDict = dict()
        self.subroutineVariables = dict()
        self.directory = directory
        self.shaderFiles = shaderFiles
        self.shaderTypes = shaderTypes
        self.defineShadersTypes(self.shaderTypes)
        for index, file in enumerate(shaderFiles):
            self.compyleShader(file, self.shaderTypes[index])
        self.createShaderProgram()
        self.searchForUniformVariables()
        logger.info(f"Shaders compiled")

    def defineShadersTypes(self, array) -> None:
        """Function for define type of shader."""
        for index, s_type in enumerate(list(array)):
            match s_type:
                case 'VERTEX':
                    array[index] = self.VERTEX
                case 'FRAGMENT':
                    array[index] = self.FRAGMENT
                case 'GEOMETRY':
                    array[index] = self.GEOMETRY
                case 'TESS_CONTROL':
                    array[index] = self.TESS_CONTROL
                case 'TESS_EVALUATION':
                    array[index] = self.TESS_EVALUATION
                case 'COMPUTE':
                    array[index] = self.COMPUTE
                case _:
                    raise VRShaderError('Error in names of shader types.')

    def compyleShader(self, file, shaderType) -> None:
        """Compiles shaders and raise errors if compilation is not succeed."""
        shader = glCreateShader(shaderType)
        if shader == 0:
            raise VRShaderError('Cannot load shader.')
        glShaderSource(shader, self.loadShaderInfo(file))
        glCompileShader(shader)
        status = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if not status:
            raise VRShaderError(f'Error while compiling {shaderType} shader.')
        self.shaders[shader] = True

    def loadShaderInfo(self, file):
        """Reads shader file and save it in string variable."""
        path = os.path.join(self.directory, file) if self.directory else file
        try:
            f = open(path, 'r', encoding="utf-8", errors='ignore')
        except:
            raise VRShaderError(f'File {path} does not exist.')
        else:
            f.close()
        shaderSource = ""
        with open(path) as f:
            shaderSource = f.read()
        return str.encode(shaderSource)

    def deleteShader(self, shader) -> None:
        if shader in self.shaders:
            glDeleteShader(shader)
            self.shaders[shader] = False

    def createShaderProgram(self) -> None:
        """Creates program and add shaders to it."""
        try:
            self.program = glCreateProgram()
        except Exception as e:
            raise VRShaderError(f'Exception: {traceback.format_exc()}.')
        if not self.program:
            raise VRShaderError('Cannot create program.')
        for shader in self.shaders:
            if self.shaders[shader]:
                glAttachShader(self.program, shader)  # Connect shaders into program
        glLinkProgram(self.program)  # Join the flats program
        status = glGetProgramiv(self.program, GL_LINK_STATUS)
        if not status:
            raise VRShaderError('Error with linking program.')

    def deleteProgram(self) -> None:
        if self.program:
            glDeleteProgram(self.program)
            self.program = 0

    def __add__(self, other: list[str, str]):
        """Function to add a new type of shader to class object."""
        try:
            file, shaderType = other
        except:
            raise VRShaderError('Add function requires pair of file, shader type.')
        shaderType = [shaderType]
        self.defineShadersTypes(shaderType)
        if shaderType[0] in self.shaderTypes:
            raise VRShaderError('Shader is already exist.')
        else:
            self.shaderTypes.append(*shaderType)
            self.shaderFiles.append(file)

    def deleteShaderFile(self, file) -> None:
        ind = self.shaderFiles.index(file)
        self.shaderFiles.pop(ind)
        self.shaderTypes.pop(ind)

    def searchForUniformVariables(self) -> None:
        """Automatically define uniform variables in shader and save it in dictionary."""
        numUniforms = glGetProgramInterfaceiv(self.program, GL_UNIFORM, GL_ACTIVE_RESOURCES)
        types = [GL_NAME_LENGTH, GL_TYPE, GL_LOCATION, GL_BLOCK_INDEX]
        for i in range(numUniforms):
            # results = np.zeros(4)
            results = glGetProgramResourceiv(self.program, GL_UNIFORM, i, 4, types, 4, None)[-1]
            if results[-1] != -1:
                continue
            nameBufSize = results[0] + 1
            name = glGetProgramResourceName(self.program, GL_UNIFORM, i, nameBufSize, None)[-1]
            name = ''.join([chr(int(el)) for el in name][:-2])
            typeName = ''
            for file in self.shaderFiles:
                with open(os.path.join(self.directory, file) if self.directory else file, 'r') as f:
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        if name in line:
                            typeName = line.split()[1]
                            break
                if typeName:
                    break
            self.uniformVariablesDict[(name, typeName)] = results[2]

    def searchSubroutineLocation(self, variableName, variable, shader: [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER, ...]) -> None:
        """Searching for any subroutines in program."""
        if self.subroutineVariables.get(variableName, None) is not None:
            self.subroutineVariables.pop(variableName)
        self.subroutineVariables[variableName] = glGetSubroutineIndex(self.program, shader, variable)

    def __call__(self) -> int:
        """Returns program ID."""
        return self.program


class VRShaderError(Exception):
    """Class for processing of errors in VRShader class."""
    def __init__(self, message):
        """Initializing function."""
        super(VRShaderError, self).__init__('Error in VRShaders occurs.\nMessage:' + message)
