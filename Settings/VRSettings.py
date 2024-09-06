import os
import json
import numpy as np
from Logs.VRLogger import sendDataToLogger


class VRSettings:

    @sendDataToLogger
    def __init__(self, logger, projectDirectory):
        self.__loger = logger
        self.__projectDirectory = projectDirectory
        self.printWindowLocation = None
        self.visualWindowLocation = None
        self.processingWindowLocation = None
        self.graphProcWindowLocation = None
        self.fileSharingWindowLocation = None
        self.consoleWindowLocation = None
        self.chgcarWindowLocation = None
        self.formPoscarWindowLocation = None
        self.oszicarWindowLocation = None
        self.bondsWindowLocation = None
        self.delCoordsLeaveCell = True
        self.lightSettings = {'POSITIONS': np.zeros((8, 4)).tolist(), 'INTENSITIES': np.zeros((8, 3)).tolist()}
        self.setStandardLight()
        self.backgroundColor = (0.0, 0.0, 0.0, 1.0)
        self.viewAxes = True
        self.viewCell = True
        self.onlyKeyboardSel = True

    def getLogger(self):
        return self.__loger

    @sendDataToLogger
    def setStandardLight(self):
        self.lightSettings['POSITIONS'][0] = [10.0, 10.0, 10.0, 0.0]
        self.lightSettings['INTENSITIES'][0] = [0.4, 0.4, 0.4]

    @sendDataToLogger
    def loadSettings(self):
        try:
            with open(self.__projectDirectory + r'\Settings\settings.json', 'r') as file:
                data = json.load(file)
            self.printWindowLocation = data['printWindowLocation']
            self.visualWindowLocation = data['visualWindowLocation']
            self.processingWindowLocation = data['processingWindowLocation']
            self.graphProcWindowLocation = data['graphProcWindowLocation']
            self.fileSharingWindowLocation = data['fileSharingWindowLocation']
            self.consoleWindowLocation = data['consoleWindowLocation']
            self.chgcarWindowLocation = data['chgcarWindowLocation']
            self.formPoscarWindowLocation = data['formPoscarWindowLocation']
            self.oszicarWindowLocation = data['oszicarWindowLocation']
            self.bondsWindowLocation = data['bondsWindowLocation']
            self.delCoordsLeaveCell = data['delCoordsLeaveCell']
            self.lightSettings = data['lightSettings']
            self.backgroundColor = data['backgroundColor']
            self.viewAxes = data['viewAxes']
            self.viewCell = data['viewCell']
            self.onlyKeyboardSel = data['onlyKeyboardSel']
        except FileNotFoundError:
            pass
        except KeyError:
            with open(self.__projectDirectory + r'\Settings\settings.json', 'w') as file:
                file.write('')
        return self

    def saveSettings(self, loger):
        loger.insertLogs(self.__class__.__name__, 'saveSettings', result='IN PROGRESS')
        variables = vars(self)
        variables.pop('_VRSettings__loger')
        with open(self.__projectDirectory + r'\Settings\settings.json', 'w') as file:
            json.dump(variables, file)
        loger.insertLogs(self.__class__.__name__, 'saveSettings')
        return self

    def __repr__(self):
        variablesDict = vars(self)
        variablesDict.pop('_VRSettings__loger')
        infoString = '{\n'
        for variable in variablesDict:
            infoString += f'{variable}: {variablesDict[variable]},\n'
        infoString += '}'
        return f"""VaspReader settings option with variables:\n{infoString}."""
