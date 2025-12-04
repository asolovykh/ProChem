class QEMD:
    """
    Initializes the Calculation object.
    
    Args:
        directory: The directory containing the calculation files.
        logger: A logger object for logging messages.
    
    Initializes the following object properties:
        self.__logger: A logger object for logging messages.
        self.directory: The directory containing the calculation files.
        self.calculationFiles: A dictionary to store calculation files.
        self.dirToReadFiles:  The directory to read files from (initialized to None).
        self.inputFile: The input file (initialized to None).
        self.breaker: A boolean flag indicating if an error occurred during initialization (initialized to False).
        self.numberOfAtomTypes: The number of atom types (initialized to 0).
        self.massesLabels: A dictionary to store atom mass labels (initialized to an empty dictionary).
        self._parserParameters: A dictionary to store parsed parameters from the input files (initialized with the directory).
    
    Returns:
        None
    """
    __atomicUnitsDistanceConstant = 1.889725988579
    __atomicUnitsTimeConstantToFs = 0.024189

    def __init__(self, directory, logger):
        """
        Initializes the Calculation object.
        
        Args:
            directory: The directory containing the calculation files.
            logger: A logger object for logging messages.
        
        Initializes the following object properties:
            self.__logger: A logger object for logging messages.
            self.directory: The directory containing the calculation files.
            self.calculationFiles: A dictionary to store calculation files.
            self.dirToReadFiles:  The directory to read files from (initialized to None).
            self.inputFile: The input file (initialized to None).
            self.breaker: A boolean flag indicating if an error occurred during initialization (initialized to False).
            self.numberOfAtomTypes: The number of atom types (initialized to 0).
            self.massesLabels: A dictionary to store atom mass labels (initialized to an empty dictionary).
            self._parserParameters: A dictionary to store parsed parameters from the input files (initialized with the directory).
        
        Returns:
            None
        """
        self.__logger = logger
        self.directory = directory
        self.calculationFiles = dict()
        self.dirToReadFiles = None
        self.inputFile = None
        self.breaker = False
        self.numberOfAtomTypes = 0
        self.massesLabels = dict()
        self._parserParameters = {'DIRECTORY': directory, 'ATOMNAMES': [], 'ATOMSINFO': dict(), 'POTIM': [], 'STEPS_LIST': [], 'POSITIONS': [], 'POMASS': [], 'MASSES': [], 'CALC_TYPE': 'QE'}
        if self.checkForQEFiles(self.directory):
            self.readCellFile()
            self.read_coord_file()
            self.readInputFile()
            formAtomsWithNumsDict(self._parserParameters)
            self._parserParameters = atomsInfoFilling(self._parserParameters)
            self._parserParameters['ID'] = [self._parserParameters['ATOMNAMES'][ind] + "_" + str(ind + 1) for ind in range(self._parserParameters['ATOMNUMBER'])]
            self._parserParameters['ID-TO-NUM'] = {self._parserParameters['ATOMNAMES'][ind] + "_" + str(ind + 1): ind for ind in range(self._parserParameters['ATOMNUMBER'])}
            self.potimToFs()
        else:
            self.breaker = True

    def getLogger(self):
        """
        Returns the logger instance.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The logger instance used for logging.
        """
        return self.__logger

    def __call__(self, *args, **kwargs):
        """
        Returns the parser parameters.
        
        Args:
            self: The instance of the class.
        
        Returns:
            The parser parameters stored in the _parserParameters field.
        """
        return self._parserParameters

    def potimToFs(self):
        """
        Converts POTIM values from internal units to femtoseconds.
        
        This method iterates through the POTIM values stored in the _parserParameters dictionary and converts each value from internal units to femtoseconds using the __atomicUnitsTimeConstantToFs conversion factor. The updated values overwrite the original values in the dictionary.
        
        Args:
            self:  The instance of the class.
        
        Returns:
            None
        """
        for num, potim in enumerate(self._parserParameters['POTIM']):
            self._parserParameters['POTIM'][num] = potim / self.__atomicUnitsTimeConstantToFs

    def cartesianToDirect(self):
        """
        Converts positions from Cartesian to direct coordinates.
        
        This method transforms the positions stored in the parser parameters from
        Cartesian coordinates to direct coordinates using the inverse of the basis
        vectors. It then adjusts the coordinates by subtracting 0.5 and calls
        the directToCartesian method to update related parameters.
        
        Args:
            self: The instance of the class.
        
        Attributes Initialized:
            _parserParameters['DIRECT']: A NumPy array representing the positions in
                direct coordinates. This is calculated by transforming the Cartesian
                positions using the inverse of the basis vectors and then adjusting
                the values.
        
        Returns:
            None
        """
        self._parserParameters['DIRECT'] = np.array([np.dot(self._parserParameters['POSITIONS'], np.linalg.inv(self._parserParameters['BASIS']))])[0]
        self._parserParameters['DIRECT'] = self._parserParameters['DIRECT'] - 0.5
        self.directToCartesian()

    def directToCartesian(self):
        """
        Calculates the cartesian positions based on direct and basis vectors.
        
        Args:
            self: The instance of the class.
        
        Initializes:
            self._parserParameters['POSITIONS']: A NumPy array representing the calculated cartesian positions.
        
        Returns:
            None.
        """
        self._parserParameters['POSITIONS'] = np.array([np.dot(self._parserParameters['DIRECT'], self._parserParameters['BASIS'])])[0]

    def checkForQEFiles(self, directory):
        """
        Checks for required Quantum Espresso input files within a directory.
        
        This method recursively searches a directory for files necessary for
        Quantum Espresso calculations. It identifies input files, velocity,
        position, and cell files, and stores their names.
        
        Args:
         self:  The instance of the class.
         directory: The path to the directory to search.
        
        Returns:
         bool: True if all required files are found, False otherwise.
        
        Class Fields Initialized:
         inputFile: The name of the input file (string).
         calculationFiles: A dictionary storing the names of velocity, position,
          and cell files, with the file extension as the key (dict).
         dirToReadFiles: The directory where all required files are found (string).
        """
        files = os.listdir(directory)
        folders = []
        requirements = ['vel', 'pos', 'cel']
        for file in files:
            extension = file.split('.')[-1]
            if extension == file and os.path.isdir(directory + '/' + file):
                folders.append(file)
            elif extension == 'in' and not self.inputFile:
                self.inputFile = file
            elif extension in requirements:
                requirements.remove(extension)
                self.calculationFiles[extension] = file
        if not requirements:
            self.dirToReadFiles = directory
            return True
        else:
            for folder in folders:
                result = self.checkForQEFiles(directory + '/' + folder)
                if result:
                    return True
            return False

    def read_coord_file(self):
        """
        Reads coordinate data from a file and populates parser parameters.
        
        This method reads a coordinate file line by line, extracts positional and timing
        information, and stores it in the `_parserParameters` dictionary. It calculates
        time steps and converts positions based on atomic units.
        
        Args:
         self: The instance of the class.
        
        Attributes Initialized:
         _parserParameters: A dictionary to store parsed parameters.
           'STEPS_LIST': A list of step counters.
           'POTIM': A list of time intervals between steps.
           'POSITIONS': A NumPy array of positional data.
           'STEPS': The total number of steps.
        
        Returns:
         None
        """
        stepsCounter = 0
        nowPotim = None
        prevTime = None
        tempArray = []
        with open(self.dirToReadFiles + '\\' + self.calculationFiles['pos']) as coord:
            while True:
                line = coord.readline()
                lineInfo = line.split()
                if not line:
                    break
                if len(lineInfo) == 2:
                    if nowPotim is None:
                        nowPotim = float(lineInfo[-1])
                        prevTime = nowPotim
                        self._parserParameters['POTIM'].append(nowPotim)
                    else:
                        nowTime = float(lineInfo[-1])
                        if round((nowTime - prevTime), 6) != round(nowPotim, 6):
                            nowPotim = nowTime - prevTime
                            self._parserParameters['STEPS_LIST'].append(stepsCounter)
                            self._parserParameters['POTIM'].append(nowPotim)
                        prevTime = nowTime
                    stepsCounter += 1
                    if tempArray:
                        self._parserParameters['POSITIONS'].append(tempArray)
                        tempArray = []
                else:
                    tempArray.append(list(map(float, lineInfo)))
            if tempArray:
                self._parserParameters['POSITIONS'].append(tempArray)
        self._parserParameters['STEPS_LIST'].append(stepsCounter)
        self._parserParameters['STEPS'] = stepsCounter - 1
        self._parserParameters['POSITIONS'] = np.array(self._parserParameters['POSITIONS']) / self.__atomicUnitsDistanceConstant
        self.cartesianToDirect()

    def readCellFile(self):
        """
        Reads data from the cell file and initializes relevant parameters.
        
         This method opens the cell file specified by the `self.dirToReadFiles` and
         `self.calculationFiles['cel']` attributes, reads basis information,
         and calculates the vertices of the unit cell.
        
         Parameters:
          self: The instance of the class.
        
         Initializes:
          _parserParameters['BASIS']: A NumPy array representing the basis vectors
           of the unit cell, normalized by the atomic units distance constant.
          _parserParameters['BASIS_VERT']: A NumPy array containing the coordinates
           of the unit cell vertices, calculated by transforming the cube vertices
           using the basis vectors.
        
         Returns:
          None
        """
        with open(self.dirToReadFiles + '\\' + self.calculationFiles['cel']) as cell:
            cell.readline()
            self._parserParameters['BASIS'] = np.array([list(map(float, cell.readline().split())), list(map(float, cell.readline().split())), list(map(float, cell.readline().split()))])
            self._parserParameters['BASIS'] = self._parserParameters['BASIS'] / self.__atomicUnitsDistanceConstant
            cubeVert = [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5],
                         [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, 0.5],
                         [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]]
            # Создание вершин границы ячейки
            self._parserParameters['BASIS_VERT'] = np.dot(np.asarray(cubeVert), self._parserParameters['BASIS'])

    def readInputFile(self):
        """
        Reads input file and parses necessary parameters.
        
        Args:
         self: The instance of the class.
        
        Initializes the following class fields:
         _parserParameters: A dictionary to store parsed parameters from the input file.
           ATOMNUMBER: The total number of atoms in the system.
           POMASS: A list of atomic masses.
           ATOMNAMES: A list of atom names.
           MASSES: A list of atomic masses corresponding to each atom.
         numberOfAtomTypes: The number of different atom types in the system.
         massesLabels: A dictionary mapping atom names to their corresponding masses.
        
        Returns:
         None
        """
        with open(self.directory + '\\' + self.inputFile) as inp:
            while True:
                line = inp.readline()
                if not line:
                    break
                elif 'nat' in line:
                    self._parserParameters['ATOMNUMBER'] = int(line.split('nat')[-1].split()[1].split(',')[0])
                elif 'ntyp' in line:
                    self.numberOfAtomTypes = int(line.split('ntyp')[-1].split()[1].split(',')[0])
                elif 'ATOMIC_SPECIES' in line:
                    for _ in range(self.numberOfAtomTypes):
                        info = inp.readline().split()[:2]
                        self._parserParameters['POMASS'].append(float(info[-1].split('d')[0]))
                        self.massesLabels[info[0]] = float(info[-1].split('d')[0])
                elif 'ATOMIC_POSITIONS' in line:
                    for _ in range(self._parserParameters['ATOMNUMBER']):
                        info = inp.readline().split()[0]
                        self._parserParameters['ATOMNAMES'].append(info)
                        self._parserParameters['MASSES'].append(self.massesLabels[info])
