import os, json, sqlite3

TABLE_BAW_PROCESS_INSTANCES = '''
    CREATE TABLE BAW_PROCESS_INSTANCES (
        PID            TEXT    PRIMARY KEY UNIQUE NOT NULL,
        NAME           TEXT    NOT NULL,
        DATA           JSON    NOT NULL
    );
    '''

INSERT_PROCESS_INSTANCE = '''
    INSERT INTO BAW_PROCESS_INSTANCES (PID, NAME, DATA) VALUES (?, ?, ?);
    '''

SELECT_PROCESS_INSTANCE = '''
    SELECT PID, NAME, JSON_EXTRACT(DATA, '$.name'), JSON_EXTRACT(DATA, '$.age') FROM BAW_PROCESS_INSTANCES;
    '''

DELETE_PROCESS_INSTANCES = """
    DELETE FROM BAW_PROCESS_INSTANCES;
    """

def createDbAndSchema(dbName):
    isNew = not os.path.exists(dbName)
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    if isNew:
        print("Opened database successfully");
        cursor.execute(TABLE_BAW_PROCESS_INSTANCES)
        conn.commit()
        print("Table created successfully")
        print(TABLE_BAW_PROCESS_INSTANCES)
    else:
        cursor.execute(DELETE_PROCESS_INSTANCES)
        conn.commit()
    conn.close()

def addRecord(dbName, pid, name, jsObj):
    data = jsObj
    if type(data) == dict:
        data = json.dumps(jsObj)

    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    print("Opened database successfully");

    count = cursor.execute(INSERT_PROCESS_INSTANCE, (pid, name, data))
    conn.commit()
    print("Row inserted successfully", count)

    conn.close()

def queryAll(dbName):
    conn = sqlite3.connect(dbName)
    cursor = conn.cursor()
    cursor.execute(SELECT_PROCESS_INSTANCE)
    records = cursor.fetchall()
    print("Total rows are:  ", len(records))
    print("Printing each row")
    row : tuple = None
    for row in records:
        #print(type(row), row)
        print("PID: ", row[0])
        print("NAME: ", row[1])
        print("name: ", row[2])
        print("age: ", row[3])
        print()
    conn.close()

#-----------------------------

#---------------------
dbName = 'test1.db'
createDbAndSchema(dbName)

for i in range(5):
    addRecord(dbName, str(i), 'Proc'+str(i), {'name':'Marco'+str(i), 'age': 59})

queryAll(dbName)

