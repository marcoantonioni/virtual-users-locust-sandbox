import bawsys.bawUniTestScenarioSqliteExport as exporter
import json

exp = exporter.TestScenarioSqliteExporter("/home/marco/locust/studio/virtual-users-locust-sandbox/outputdata/unittest-scenario1-sqlite.db")
instances = exp.queryAll()
for i in instances:
    print(json.dumps(i, indent=2))

print("------------------")

instances : dict = exp.queryAll(asDict=True)
keys = instances.keys()
for k in keys:
    print(k)
    print(json.dumps(instances[k], indent=2))

