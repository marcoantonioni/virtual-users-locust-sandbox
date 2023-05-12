import json, logging
from jsonpath_ng.ext import parse
from bawsys import loadEnvironment as bpmEnv

class ScenarioAsserter:

    def __init__(self, bpmEnvironment : bpmEnv.BpmEnvironment):
        self.bpmEnvironment = bpmEnvironment
        self.__log = False
        self.failures = []


    #====================================
    # Utilities
    #====================================

    """
    Returns a list of items where values matches
    """
    def _queryGetMatchingRecords(self, items, _variable: str, _operator: str, _value: str):
        strQuery = "$[?"+_variable+" "+_operator+" " + _value + "]"
        jpQuery = parse(strQuery)
        return [match.value for match in jpQuery.find(items)]

    """
    Returns a list of process instances in the state defined by the input variable
    """
    def _queryGetAllInstancesByState(self, listOfInstances, state: str):
        strQuery = "$[?(@.state=='"+state+"')]"
        jpQuery = parse(strQuery)
        return [match.value for match in jpQuery.find(listOfInstances)]

    """
    Returns a list of variables of all processes in the state defined by the input variable
    """
    def _queryGetVariablesFromAllInstancesByState(self, listOfInstances, state: str):
        strQuery = "$[?(@.state=='"+state+"')].variables"
        jpQuery = parse(strQuery)
        return [match.value for match in jpQuery.find(listOfInstances)]

    """
    Returns a list of process instances where values matches
    """
    def _queryGetGetAllInstancesByMatchingValue(self, listOfInstances, _variable: str, _operator: str, _value: str):
        strQuery = "$[?variables."+_variable+" "+_operator+" " + _value + "]"
        jpQuery = parse(strQuery)
        return [match.value for match in jpQuery.find(listOfInstances)]

    """
    Returns a list of variables where values matches
    """
    def _queryGetVariablesFromAllMatchingValue(self, listOfInstances, _variable: str, _operator: str, _value: str):
        strQuery = "$[?variables."+_variable+" "+_operator+" " + _value + "].variables"
        jpQuery = parse(strQuery)
        return [match.value for match in jpQuery.find(listOfInstances)]


    #====================================
    # Assertions
    #====================================
    
    def assertItemsCountEquals(self, items, count: int):
        _asserted = len(items) == count
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertItemsCountEquals.__name__, count])

    def assertEqual(self, items, var: str, val: str):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "=", val)
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertEqual.__name__, var, val])

