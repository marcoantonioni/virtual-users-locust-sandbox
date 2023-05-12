import json, logging

from jsonpath_ng.ext import parse

__log = False


#-------------------------------------

def _queryGetMatchingRecords(listOfInstances, _variable: str, _operator: str, _value: str):
    strQuery = "$[?"+_variable+" "+_operator+" " + _value + "]"
    jpQuery = parse(strQuery)
    return [match.value for match in jpQuery.find(listOfInstances)]

#-------------------------------------


__failed = []

def assertItemsCountEquals(items, count: int):
    _asserted = len(items) == count
    if not _asserted:
        __failed.append([assertItemsCountEquals.__name__, count])

def assertEqual(items, var: str, val: str):
    totItems = len(items)
    matches = _queryGetMatchingRecords(items, var, "=", val)
    _asserted = len(matches) == totItems
    if not _asserted:
        __failed.append([assertEqual.__name__, var, val])

def executeAsserts(listOfInstances):
    logging.info("======> executeAsserts, tot instances: %d", len(listOfInstances))
    if __log:
        logging.info(json.dumps(listOfInstances, indent=2))

    assertItemsCountEquals(listOfInstances, 2)
    assertEqual(listOfInstances, "variables.promoteRequest", "false")

    if len(__failed) == 0:
        print("\nTEST OK")
    else:
        print("\nTEST FAILED\n\nItems", len(listOfInstances), "\n", json.dumps(listOfInstances, indent=2), "\n\nfailures", len(__failed), "\n", json.dumps(__failed, indent=2))