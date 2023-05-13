import json, logging

from jsonpath_ng.ext import parse

from bawsys import bawUniTestScenarioAsserter as scenAssert



__log = True


#---------------------------------------------------------
# Process instances
#---------------------------------------------------------

def exampleGetInstancesInState(asserter: scenAssert.ScenarioAsserter, listOfInstances):
    matches = asserter._queryGetAllInstancesByState(listOfInstances, "Active")
    
    logging.info("exampleGetInstancesInState %d", len(matches))
    if __log:
        for match in matches:
            logging.info("exampleGetInstancesInState %s", match)


#---------------------------------------------------------
# Variables by process instance state
#---------------------------------------------------------

def exampleGetVariablesFromAllCompleted(asserter: scenAssert.ScenarioAsserter, listOfInstances):
    matches = asserter._queryGetVariablesFromAllInstancesByState(listOfInstances, "Completed")

    logging.info("exampleGetVariablesFromAllCompleted %d", len(matches))
    if __log:
        for match in matches:
            logging.info("exampleGetVariablesFromAllCompleted %s", match)

def exampleGetVariablesFromAllActive(asserter: scenAssert.ScenarioAsserter, listOfInstances):
    matches = asserter._queryGetVariablesFromAllInstancesByState(listOfInstances, "Active")

    logging.info("exampleGetVariablesFromAllActive %d", len(matches))
    if __log:
        for match in matches:
            logging.info("exampleGetVariablesFromAllActive %s", match)


#---------------------------------------------------------
# Queries with comparison operator
#---------------------------------------------------------

def exampleGetVariablesFromAllCounterLessOrEqualThan(asserter: scenAssert.ScenarioAsserter, listOfInstances, threshold: int):
    matches = asserter._queryGetVariablesFromAllMatchingValue(listOfInstances, "inputData.newCounter", "<=", str(threshold))

    logging.info("exampleGetVariablesFromAllCounterLessOrEqualThan %d %d", len(matches), threshold)
    if __log:
        for match in matches:
            logging.info("exampleGetVariablesFromAllCounterLessOrEqualThan %s", match)


def exampleGetVariablesFromAllCounterGreaterThan(asserter: scenAssert.ScenarioAsserter, listOfInstances, threshold: int):
    matches = asserter._queryGetVariablesFromAllMatchingValue(listOfInstances, "inputData.newCounter", ">", str(threshold))

    logging.info("exampleGetVariablesFromAllCounterGreaterThan %d %d", len(matches), threshold)
    if __log:
        for match in matches:
            logging.info("exampleGetVariablesFromAllCounterGreaterThan %s", match)


#---------------------------------------------------------
# Queries with logical operators and and or
#---------------------------------------------------------

def exampleGetVariablesFromAllCompletedAndCounterLessThan(asserter: scenAssert.ScenarioAsserter, listOfInstances, threshold: int):
    strQuery = "$[?(@.state=='Completed' & @.variables.inputData.newCounter <= " + str(threshold) + " )].variables"
    jpQuery = parse(strQuery)
    matches = [match.value for match in jpQuery.find(listOfInstances)]

    logging.info("exampleGetVariablesFromAllCompletedAndCounterLessThan %d %d", len(matches), threshold)
    if __log:
        for match in matches:
            logging.info("exampleGetVariablesFromAllCompletedAndCounterLessThan %s", match)

def exampleGetVariablesFromAllActiveAndCounterLessThan(asserter: scenAssert.ScenarioAsserter, listOfInstances, threshold: int):
    strQuery = "$[?(@.state=='Active' & @.variables.inputData.newCounter <= " + str(threshold) + " )].variables"
    jpQuery = parse(strQuery)
    matches = [match.value for match in jpQuery.find(listOfInstances)]

    logging.info("exampleGetVariablesFromAllActiveAndCounterLessThan %d %d", len(matches), threshold)
    if __log:
        for match in matches:
            logging.info("exampleGetVariablesFromAllActiveAndCounterLessThan %s", match)


def exampleCompositeQueries(asserter: scenAssert.ScenarioAsserter, listOfInstances):
    matches = asserter._queryGetVariablesFromAllInstancesByState(listOfInstances, "Active")
    print(json.dumps(matches, indent=2))
    matches2 = asserter._queryGetMatchingRecords(matches, "inputData.newCounter", "<", "51")

    logging.info("exampleCompositeQueries first[%d] second[%d]", len(matches), len(matches2))
    if __log:
        for match in matches2:
            logging.info("exampleCompositeQueries %s", match)


#---------------------------------------------------------
# Main function
#---------------------------------------------------------

def executeAsserts(asserter: scenAssert.ScenarioAsserter, listOfInstances):
    logging.info("======> executeAsserts, tot instances: %d", len(listOfInstances))
    if __log:
        logging.info(json.dumps(listOfInstances, indent=2))

    exampleGetInstancesInState(asserter, listOfInstances)
    exampleGetVariablesFromAllCompleted(asserter, listOfInstances)
    exampleGetVariablesFromAllActive(asserter, listOfInstances)
    exampleGetVariablesFromAllCounterLessOrEqualThan(asserter, listOfInstances, 50)
    exampleGetVariablesFromAllCounterGreaterThan(asserter, listOfInstances, 50)
    exampleGetVariablesFromAllCompletedAndCounterLessThan(asserter, listOfInstances, 100)
    exampleGetVariablesFromAllActiveAndCounterLessThan(asserter, listOfInstances, 100)

    exampleCompositeQueries(asserter, listOfInstances)

"""
with open('./outputdata/unittest-scenario1-bis.json') as f:
    d = json.load(f)
    # logging.info(json.dumps(d, indent=2))

    jeState = parse('$[*].DATA.state')
    jeAuthData = parse('$[*].DATA.variables.authorizationData')    

    jeCounter = parse("$[?(@.DATA.variables.inputData.newCounter < 70)].PID")
    
    for match in jeState.find(d):
        logging.info(f'state: {match.value}')

    logging.info()
    for match in jeAuthData.find(d):
        logging.info(f'authData: {match.value}')

    logging.info()
    for match in jeCounter.find(d):
        logging.info(f'counter: {match.value}')
"""


"""
with open('/home/marco/locust/studio/virtual-users-locust-sandbox/outputdata/movies.json') as movies_json:
	movies = json.load(movies_json)
	
# query = "$.movies[?(@.cast[:] =~ 'De Niro')].title"
query = "$[?(@.year < 1995)].title"

jsonpath_expression = parse(query)

for match in jsonpath_expression.find(movies):
    logging.info(match.value)
"""


"""
import json
from jsonpath_ng import jsonpath, parse

# Define your JSON data
data = {
    "books": [
        {
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "year": 1951,
            "genre": "Fiction"
        },
        {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "year": 1960,
            "genre": "Fiction"
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "year": 1949,
            "genre": "Fiction"
        }
    ]
}

# Define your JSONPath expression
expression = parse("$.books[?(@.author=='J.D. Salinger' and @.year==1951 or @.genre=='Fiction')].title, $.books[?(@.author=='J.D. Salinger' and @.year==1951 or @.genre=='Fiction')].year")

# Apply the JSONPath expression to the JSON data
matches = [match.value for match in expression.find(data)]

# Print the results
logging.info(matches)

"""