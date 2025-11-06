class QEMD:
    __atomicUnitsDistanceConstant = 1.889725988579
    __atomicUnitsTimeConstantToFs = 0.024189

    def __init__(self, directory, logger):
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
        return self.__logger

    def __call__(self, *args, **kwargs):
        return self._parserParameters

    def potimToFs(self):
        for num, potim in enumerate(self._parserParameters['POTIM']):
            self._parserParameters['POTIM'][num] = potim / self.__atomicUnitsTimeConstantToFs

    def cartesianToDirect(self):
        self._parserParameters['DIRECT'] = np.array([np.dot(self._parserParameters['POSITIONS'], np.linalg.inv(self._parserParameters['BASIS']))])[0]
        self._parserParameters['DIRECT'] = self._parserParameters['DIRECT'] - 0.5
        self.directToCartesian()

    def directToCartesian(self):
        self._parserParameters['POSITIONS'] = np.array([np.dot(self._parserParameters['DIRECT'], self._parserParameters['BASIS'])])[0]

    def checkForQEFiles(self, directory):
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
