import os
import copy
import random
import traceback
import numpy as np


def deletedPositionsToNone(directPositionsArray, positionsArray):
    for step in range(len(directPositionsArray)):
        for atom in range(len(directPositionsArray[step])):
            for proj in range(len(directPositionsArray[step][atom])):
                if directPositionsArray[step][atom][proj] == 10.:
                    positionsArray[step][atom][proj] = None


def atomsInfoFilling(dictionary):
    dictionary['RADII'] = []
    for _, name in enumerate(set(dictionary['ATOMNAMES'])):
        dictionary['ATOMSINFO'][name] = {'COLORVALUE': [], 'RADII': 1, 'FILLED': False}

    for i in range(dictionary['ATOMNUMBER']):
        atom = dictionary['ATOMNAMES'][i]
        nowFillingAtom = dictionary['ATOMSINFO'][dictionary['ATOMNAMES'][i]]
        if not nowFillingAtom['FILLED']:
            if atom == 'O':
                nowFillingAtom['COLORVALUE'] = np.asarray([1, 0, 0]) # 'red'
                nowFillingAtom['RADII'] = 0.3
            elif atom == 'Si':
                nowFillingAtom['COLORVALUE'] = np.asarray([1, 1, 0])  # 'yellow'
                nowFillingAtom['RADII'] = 0.4
            elif atom == 'H':
                nowFillingAtom['COLORVALUE'] = np.asarray([0.5, 0.5, 0.5])  # 'gray'
                nowFillingAtom['RADII'] = 0.2
            elif atom == 'C':
                nowFillingAtom['COLORVALUE'] = np.asarray([0.2, 0.2, 0.2])  # 'black'
                nowFillingAtom['RADII'] = 0.33
            elif atom == 'He':
                nowFillingAtom['COLORVALUE'] = np.asarray([0, 1, 0])  # 'green'
                nowFillingAtom['RADII'] = 0.18
            elif atom == 'Ar':
                nowFillingAtom['COLORVALUE'] = np.asarray([0.6, 0, 0.6])  # 'purple'
                nowFillingAtom['RADII'] = 0.34
            elif atom == 'Xe':
                nowFillingAtom['COLORVALUE'] = np.asarray([0.05, 0, 0.6])  # 'blue'
                nowFillingAtom['RADII'] = 0.38
            elif atom == 'Mo':
                nowFillingAtom['COLORVALUE'] = np.asarray([0, 0.78, 0.78]) # old violet 0.63, 0, 0.63 '#00c6c6' #a100a1
                nowFillingAtom['RADII'] = 0.5
            elif atom == 'S':
                nowFillingAtom['COLORVALUE'] = np.asarray([1.0, 1.0, 0])  # '#ffff00'
                nowFillingAtom['RADII'] = 0.36
            elif atom == 'N':
                nowFillingAtom['COLORVALUE'] = np.asarray([0, 0, 1]) # old light blue '#0000ff'
                nowFillingAtom['RADII'] = 0.24
            elif atom == 'Ne':
                nowFillingAtom['COLORVALUE'] = np.asarray([0.543, 0.27, 0.07])  # '#8b4513'
                nowFillingAtom['RADII'] = 0.16
            elif atom == 'Cl':
                nowFillingAtom['COLORVALUE'] = np.asarray([0.12, 0.77, 0.65])  # '1fc4a6'
                nowFillingAtom['RADII'] = 0.3
            else:
                r, g, b = random.random(), random.random(), random.random()
                rad = random.uniform(0.24, 0.42)
                nowFillingAtom['COLORVALUE'] = np.asarray([r, g, b])
                nowFillingAtom['RADII'] = rad
            nowFillingAtom['FILLED'] = True


    for i in range(dictionary['ATOMNUMBER']):
        dictionary['RADII'].append(dictionary['ATOMSINFO'][dictionary['ATOMNAMES'][i]]['RADII'])
    return dictionary


def formAtomsWithNumsDict(parserParameters):
    parserParameters['ATOM-NUMBERS'] = dict()
    for uniqAtom in set(parserParameters['ATOMNAMES']):
        for number, atom in enumerate(parserParameters['ATOMNAMES']):
            if atom == uniqAtom:
                strippedAtom = uniqAtom.rstrip()
                if strippedAtom in parserParameters['ATOM-NUMBERS']:
                    parserParameters['ATOM-NUMBERS'][strippedAtom].append(number)
                else:
                    parserParameters['ATOM-NUMBERS'][strippedAtom] = [number]
    for key in parserParameters['ATOM-NUMBERS']:
        parserParameters['ATOM-NUMBERS'][key] = np.array(parserParameters['ATOM-NUMBERS'][key])


class VRMD:

    def __init__(self, directory, parserParametersDict):
        self._parserParameters = parserParametersDict
        self._parserParameters.update({'DIRECTORY': directory, 'ATOMSINFO': dict(), 'CALC_TYPE': 'VASP', 'BREAKER': False, 'MESSAGE': ''})
        self.XMLLIST = []
        vaspnum = 0
        try:
            for vaspfile in os.listdir(directory):
                if vaspfile.endswith('.xml'):
                    vaspnum += 1
                    self._parserParameters[vaspfile] = {'ATOMNAMES': [], 'ATOMNUMBER': 0, 'POMASS': [], 'POSITIONS': [], 'POTIM': 0., 'TYPE': []}
                    self.XMLLIST.append(vaspfile)
        except AttributeError as err:
            self._parserParameters['BREAKER'] = True
            self._parserParameters['MESSAGE'] = 'Exception occurred when watching for vaspruns in directory.\n' + traceback.format_exc()
        self.XMLLIST.sort()
        self._parserParameters['XMLLIST'] = self.XMLLIST
        if vaspnum == 0:
            self._parserParameters['BREAKER'] = True
            self._parserParameters['MESSAGE'] = 'There are no Vasprun files in the directory.'
        elif vaspnum != 0:
            for vInd in range(len(self.XMLLIST)):
                POTIMRead, BASISRead = True, True
                firstReadCheck, firstCoordRead = True, True
                with open(directory + '\\' + self.XMLLIST[vInd], 'r') as VASP:
                    while True:
                        line = VASP.readline()
                        if not line:
                            break
                        if '<atoms>' in line:
                            self._parserParameters[self.XMLLIST[vInd]]['ATOMNUMBER'] = int(line.split()[1])
                        if '<field type="int">atomtype</field>' in line:
                            VASP.readline()
                            for index in range(self._parserParameters[self.XMLLIST[vInd]]['ATOMNUMBER']):
                                atomtype = VASP.readline()
                                self._parserParameters[self.XMLLIST[vInd]]['ATOMNAMES'].append((atomtype.split('>')[2]).split('<')[0])
                                self._parserParameters[self.XMLLIST[vInd]]['TYPE'].append(int(atomtype.split('<')[4].split('>')[1]))
                        if POTIMRead and 'name="POTIM">' in line:
                            self._parserParameters[self.XMLLIST[vInd]]['POTIM'] = float(line.split()[2].split('<')[0])
                            POTIMRead = False
                        if 'name="POMASS">' in line:
                            for mass in line.split()[2:-1]:
                                self._parserParameters[self.XMLLIST[vInd]]['POMASS'].append(float(mass))
                            self._parserParameters[self.XMLLIST[vInd]]['POMASS'].append(float((line.split()[-1]).split('<')[0]))
                        if '<varray name="positions" >' in line:  # <varray name="positions" >
                            try:
                                if firstReadCheck:
                                    firstReadCheck = False
                                else:
                                    array = [list(map(float, VASP.readline().split()[1:4])) for _ in range(self._parserParameters[self.XMLLIST[vInd]]['ATOMNUMBER'])]
                                    if firstCoordRead:
                                        self._parserParameters[self.XMLLIST[vInd]]['POSITIONS'].append(array)
                                        firstCoordRead = False
                                    if array != self._parserParameters[self.XMLLIST[vInd]]['POSITIONS'][-1]:
                                        self._parserParameters[self.XMLLIST[vInd]]['POSITIONS'].append(array)
                            except Exception as err:
                                self._parserParameters['BREAKER'] = True
                                self._parserParameters['MESSAGE'] = 'There are mistakes with reading positions.\n' + traceback.format_exc()
                        if BASISRead and '<varray name="basis" >' in line:
                            basisStr = [VASP.readline() for _ in range(3)]
                            basis = [list(map(float, basisStr[index].split()[1:4])) for index in range(len(basisStr))]
                            self._parserParameters[self.XMLLIST[vInd]]['BASIS'] = basis
                            BASISRead = False
                self._parserParameters[self.XMLLIST[vInd]]['VASPLEN'] = len(self._parserParameters[self.XMLLIST[vInd]]['POSITIONS'])
            self._parserParameters['MASSES'] = [self._parserParameters[self.XMLLIST[0]]['POMASS'][index - 1] for index in self._parserParameters[self.XMLLIST[0]]['TYPE']]
            self._parserParameters['STEPS_LIST'] = [self._parserParameters[self.XMLLIST[0]]['VASPLEN']]
            for xml in self.XMLLIST[1:]:
                self._parserParameters['STEPS_LIST'].append(self._parserParameters['STEPS_LIST'][-1] + self._parserParameters[xml]['VASPLEN'] - 1)
            self._parserParameters['STEPS'] = sum([self._parserParameters[xml]['VASPLEN'] for xml in self.XMLLIST]) - len(self.XMLLIST) + 1
            self._parserParameters['ATOMNAMES'] = self._parserParameters[self.XMLLIST[0]]['ATOMNAMES']
            formAtomsWithNumsDict(self._parserParameters)
            self.removedAtomsFind(self._parserParameters)
            self.positionArrayForm(self._parserParameters)
            self._parserParameters['POTIM'] = [self._parserParameters[xml_file]['POTIM'] for xml_file in self._parserParameters['XMLLIST']]
            if not self.breaker:
                try:
                    self._parserParameters['POSITIONS'] = np.array(self._parserParameters['POSITIONS'])
                    self._parserParameters['BASIS'] = self._parserParameters[self._parserParameters['XMLLIST'][0]]['BASIS']
                    self._parserParameters['ATOMNUMBER'] = self._parserParameters[self._parserParameters['XMLLIST'][0]]['ATOMNUMBER']
                    for i in range(self._parserParameters['ATOMNUMBER']):
                        if self._parserParameters['ATOMNAMES'][i][-1] == ' ':
                            self._parserParameters['ATOMNAMES'][i] = self._parserParameters['ATOMNAMES'][i][:-1]
                    self._parserParameters['BASIS'] = np.array(self._parserParameters['BASIS'])
                    cubeVert = [[0.5, -0.5, -0.5], [0.5, 0.5, -0.5],
                                 [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5], [0.5, -0.5, 0.5],
                                 [0.5, 0.5, 0.5], [-0.5, -0.5, 0.5], [-0.5, 0.5, 0.5]]
                    # Создание вершин границы ячейки
                    self._parserParameters['BASIS_VERT'] = np.dot(np.asarray(cubeVert), self._parserParameters['BASIS'])
                    self._parserParameters['DIRECT'] = np.copy(self._parserParameters['POSITIONS'])
                    self._parserParameters['POSITIONS'] = self._parserParameters['POSITIONS'] - 0.5
                    # Преобразование координат из дискретных в декартовы в соответствии с базисом
                    for m in range(self._parserParameters['STEPS']):
                        self._parserParameters['POSITIONS'][m] = np.dot(self._parserParameters['POSITIONS'][m], self._parserParameters['BASIS'])
                    deletedPositionsToNone(self._parserParameters['DIRECT'], self._parserParameters['POSITIONS'])
                    self._parserParameters = atomsInfoFilling(self._parserParameters)
                    self._parserParameters['ID'] = [self._parserParameters['ATOMNAMES'][ind] + "_" + str(ind + 1) for ind in range(self._parserParameters['ATOMNUMBER'])]
                    self._parserParameters['ID-TO-NUM'] = {self._parserParameters['ATOMNAMES'][ind] + "_" + str(ind + 1): ind for ind in range(self._parserParameters['ATOMNUMBER'])}
                except KeyError as err:
                    self._parserParameters['BREAKER'] = True
                    self._parserParameters['MESSAGE'] = 'There are mistakes with reading positions and/or basis.\n' + traceback.format_exc()

    def __call__(self, *args, **kwargs):
        return self._parserParameters

    def removedAtomsFind(self, dictionary):
        XML = dictionary.get('XMLLIST')
        self.breaker = False
        if len(XML) > 1:
            for file in range(len(XML) - 1):
                indexF2, differ = 0, []
                for f1Element in dictionary[XML[file]]['POSITIONS'][-1]:
                    if f1Element == dictionary[XML[file + 1]]['POSITIONS'][0][indexF2]:
                        indexF2 += 1 if indexF2 < len(dictionary[XML[file + 1]]['POSITIONS'][0]) - 1 else 0
                        differ.append(False)
                        continue
                    else:
                        differ.append(True)
                dictionary[XML[file + 1]]['REMOVED'] = differ
                if file != 0:
                    for index in range(len(dictionary[XML[file]]['REMOVED'])):
                        if dictionary[XML[file]]['REMOVED'][index]:
                            dictionary[XML[file + 1]]['REMOVED'].insert(index, True)
                if sum(differ) != dictionary[XML[0]]['ATOMNUMBER'] - dictionary[XML[file + 1]]['ATOMNUMBER']:
                    self._parserParameters['BREAKER'] = True
                    self._parserParameters['MESSAGE'] = 'Vasprun files present different calculations.'

    @ staticmethod
    def positionArrayForm(dictionary):
        XML = dictionary['XMLLIST']
        dictionary['POSITIONS'] = copy.deepcopy(dictionary[XML[0]]['POSITIONS'])
        for positions in range(1, len(XML)):
            for differentPos in range(len(dictionary[XML[positions]]['REMOVED'])):
                if dictionary[XML[positions]]['REMOVED'][differentPos]:
                    for arrayValue in range(len(dictionary[XML[positions]]['POSITIONS'])):
                        dictionary[XML[positions]]['POSITIONS'][arrayValue].insert(differentPos, [10., 10., 10.])
            dictionary['POSITIONS'] += dictionary[XML[positions]]['POSITIONS'][1:]


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
