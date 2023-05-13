import logging, os, json, sqlite3

class TestScenarioSqliteExporter:

    stmtCreateTableProcessInstances = """
        CREATE TABLE BAW_PROCESS_INSTANCES (
            PID     TEXT    PRIMARY KEY UNIQUE NOT NULL,
            DATA    JSON    NOT NULL
        );
    """

    stmtCreateTableUnitTestScenario = """
        CREATE TABLE BAW_UNIT_TEST_SCENARIO (
            STARTED_AT          TEXT    NOT NULL,
            ENDED_AT            TEXT    NOT NULL,
            NUM_INSTANCES       INTEGER NOT NULL,
            TIME_LIMIT_EXCEEDED INTEGER NOT NULL,
            ASSERTS_MGR         TEXT    NOT NULL
        );
    """

    stmtInsertObject = """
        INSERT INTO BAW_PROCESS_INSTANCES (PID, DATA) VALUES (?, ?);
    """
    
    stmtInsertInfos = """
        INSERT INTO BAW_UNIT_TEST_SCENARIO (STARTED_AT, ENDED_AT, NUM_INSTANCES, TIME_LIMIT_EXCEEDED, ASSERTS_MGR) VALUES (?, ?, ?, ?, ?);
    """

    stmtQueryAllObjects = """
        SELECT PID, JSON_EXTRACT(DATA, '$') FROM BAW_PROCESS_INSTANCES;
    """

    stmtDeleteAll = """
        DELETE FROM BAW_PROCESS_INSTANCES;
    """

    def __init__(self, dbName : str):
        self.dbName = dbName
        
    def createDbAndSchema(self):
        try:
            isNew = not os.path.exists(self.dbName)
            if not isNew:
                os.remove(self.dbName)
            conn = sqlite3.connect(self.dbName)
            cursor = conn.cursor()
            cursor.execute(self.stmtCreateTableProcessInstances)
            cursor.execute(self.stmtCreateTableUnitTestScenario)
            conn.commit()
            conn.close()
        except BaseException as exception:
            logging.warning(f"Exception Name: {type(exception).__name__}")
            logging.warning(f"Exception Desc: {exception}")
            logging.error("ERROR TestScenarioSqliteExporter, createDbAndSchema")

    def setScenarioInfos(self, startedAt: str, endedAt: str, numInstances: int, timeLimitExceeded: int, assertManager: str):
        try:
            conn = sqlite3.connect(self.dbName)
            cursor = conn.cursor()
            count = cursor.execute(self.stmtInsertInfos, (startedAt, endedAt, numInstances, timeLimitExceeded, assertManager))
            conn.commit()
            conn.close()
        except BaseException as exception:
            logging.warning(f"Exception Name: {type(exception).__name__}")
            logging.warning(f"Exception Desc: {exception}")
            logging.error("ERROR TestScenarioSqliteExporter, setScenarioInfos")


    def addRecord(self, jsObj):
        if type(jsObj) == dict:
            try:
                pid = jsObj['processId']
                data = json.dumps(jsObj)
                conn = sqlite3.connect(self.dbName)
                cursor = conn.cursor()
                count = cursor.execute(self.stmtInsertObject, (pid, data))
                conn.commit()
                conn.close()
            except BaseException as exception:
                logging.warning(f"Exception Name: {type(exception).__name__}")
                logging.warning(f"Exception Desc: {exception}")
                logging.error("ERROR TestScenarioSqliteExporter, addRecord")
        else:
                logging.error("ERROR TestScenarioSqliteExporter, addRecord, not a json object")

    def addScenario(self, listOfObjs):
        for item in listOfObjs:
            instance = {}
            instance["processName"] = item.bpdName
            instance["processId"] = item.piid 
            instance["state"] = item.executionState
            instance["variables"] = item.variables
            self.addRecord(instance)

    def queryAll(self):
        instances = []
        try:
            conn = sqlite3.connect(self.dbName)
            cursor = conn.cursor()
            cursor.execute(self.stmtQueryAllObjects)
            records = cursor.fetchall()
            row : tuple = None
            for row in records:
                instances.append(json.loads(row[1]))
            conn.close()
        except BaseException as exception:
            logging.warning(f"Exception Name: {type(exception).__name__}")
            logging.warning(f"Exception Desc: {exception}")
            logging.error("ERROR TestScenarioSqliteExporter, queryAll")
        return instances
