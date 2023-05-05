import logging, os, json, sqlite3

class TestScenarioSqliteExporter:

    stmtCreateTable = """
        CREATE TABLE BAW_PROCESS_INSTANCES (
            PID     TEXT    PRIMARY KEY UNIQUE NOT NULL,
            DATA    JSON    NOT NULL
        );
    """

    stmtInsertObject = """
        INSERT INTO BAW_PROCESS_INSTANCES (PID, DATA) VALUES (?, ?);
    """
    
    stmtQueryAllObjects = """
        SELECT PID, 
                JSON_EXTRACT(DATA, '$.processName'), 
                JSON_EXTRACT(DATA, '$.processId') 
                JSON_EXTRACT(DATA, '$.state') 
                JSON_EXTRACT(DATA, '$.variables') 
            FROM BAW_PROCESS_INSTANCES;
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
            cursor.execute(self.stmtCreateTable)
            conn.commit()
            conn.close()
        except BaseException as exception:
            logging.warning(f"Exception Name: {type(exception).__name__}")
            logging.warning(f"Exception Desc: {exception}")
            logging.error("ERROR TestScenarioSqliteExporter, createDbAndSchema")

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
