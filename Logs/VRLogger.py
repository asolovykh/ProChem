import sqlite3
import traceback


def sendDataToLogger(func=None, operationType='program'):
    def wrapper(func):
        def wrappedFunc(*args):
            output = None
            try:
                args[0].getLogger().insertLogs(args[0].__class__.__name__, func.__name__, operationType, 'IN PROGRESS')
            except AttributeError:
                pass
            try:
                output = func(*args)
            except Exception as err:
                args[0].getLogger().insertLogs(args[0].__class__.__name__, func.__name__, operationType, 'FAILED', cause='Error in function', detailed_description=traceback.format_exc())
            try:
                args[0].getLogger().insertLogs(args[0].__class__.__name__, func.__name__, operationType)
            except AttributeError:
                pass
            return output
        return wrappedFunc
    if func is not None:
        return wrapper(func)
    else:
        return wrapper


class VRLogger:

    def __init__(self, dbName='logs.db'):
        self._db = sqlite3.connect(f'Logs\\{dbName}')
        self._cursor = self._db.cursor()
        self.__operationNumber = 1
        try:
            self._cursor.execute("SELECT * FROM logs LIMIT 13;").fetchall()
            self._cursor.execute("DELETE FROM logs;").fetchall()
            self._db.commit()
        except sqlite3.OperationalError:
            self._cursor.execute("CREATE TABLE logs ( NUMBER int NOT NULL UNIQUE, WINDOW text NOT NULL, "
                                 "OPERATION text NOT NULL, OPERATION_TYPE text NOT NULL, "
                                 "RESULT text NOT NULL DEFAULT 'SUCCESS', CAUSE text DEFAULT NULL, "
                                 "DETAILED_DESCRIPTION text DEFAULT NULL, DATE date NOT NULL, "
                                 "TIME time NOT NULL, CHECK (OPERATION_TYPE IN ('user', 'program')), "
                                 "CHECK (RESULT IN ('FAILED', 'IN PROGRESS', 'SUCCESS')), "
                                 "PRIMARY KEY (NUMBER) );").fetchall()

    def insertLogs(self, window: str, operation: str, operationType: str = 'program', result: str = 'SUCCESS', cause: str = None, detailedDescription: str = None):
        if cause is not None and detailedDescription is not None:
            self._cursor.execute(f"INSERT INTO logs VALUES ('{self.__operationNumber}', '{window}', '{operation}', '{operationType}', '{result}', '{cause}', '{detailedDescription}', current_date, current_time);").fetchall()
        elif cause is None and detailedDescription is not None:
            self._cursor.execute(f"INSERT INTO logs (NUMBER, WINDOW, OPERATION, OPERATION_TYPE, RESULT, DETAILED_DESCRIPTION, DATE, TIME) VALUES ('{self.__operationNumber}', '{window}', '{operation}', '{operationType}', '{result}', '{detailedDescription}', current_date, current_time);").fetchall()
        elif cause is not None and detailedDescription is None:
            self._cursor.execute(f"INSERT INTO logs (NUMBER, WINDOW, OPERATION, OPERATION_TYPE, RESULT, CAUSE, DATE, TIME) VALUES ('{self.__operationNumber}', '{window}', '{operation}', '{operationType}', '{result}', '{cause}', current_date, current_time);").fetchall()
        else:
            self._cursor.execute(f"INSERT INTO logs (NUMBER, WINDOW, OPERATION, OPERATION_TYPE, RESULT, DATE, TIME) VALUES ('{self.__operationNumber}', '{window}', '{operation}', '{operationType}', '{result}', current_date, current_time);").fetchall()
        self._db.commit()
        self.__operationNumber += 1

    def __del__(self):
        self._cursor.close()
        self._db.close()
