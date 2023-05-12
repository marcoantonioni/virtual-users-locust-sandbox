#---------------------------------------------------------
# https://scrapfly.io/blog/parse-json-jsonpath-python/
# https://blogboard.io/blog/knowledge/jsonpath-python/

"""
operator	                        function
$	                                object root selector
@ or this	                        current object selector
..	                                recursive descendant selector
*	                                wildcard, selects any key of an object or index of an array
[]	                                subscript operator
[start:end:step]	                array slice operator
[?<predicate>] or (?<predicate>)	filter operator where predicate is some evaluation rule like [?price>20], more examples:
[?price > 20 & price < 10]          multiple
[?address.city = "Boston"]          for exact matches
[?description.text =~ "house"]      for containing values

-------------------------------------------------------------------------------------------------

EXPRESSION	                EXAMPLE	                        RESULT
$	                        $	                            Selects the root object
.property or ['property']	$.movies or $['movies']	        Returns a child element or property by name
*	                        $.movies[*] or $.movies[0].*	Wildcard. .* returns all fields of an element, [*] selects all members of an array
..	                        $..year	                        Recursive descent - return all values of the given property in the structure. Here: returns all years from all movies.
[index]	                    $.movies[0]	                    Returns the child element at index
[0,1]	                    $.movies[0].cast[0,1]	        Returns the first and second child elements
[start:end]	                $.movies[0].cast[:2]	        Similar to Python list slicing syntax. Return child elements at positions start through end
@	                        See below	                    Reference to current object in filtering expressions
[?(filter)]	                $.movies[?(@.year < 1990)]	    Apply a filter to selected element. Here: Returns all movies where year < 1990


-------------------------------------------------------------------------------------------------
? : Question mark, marks the beginning of an expression. Syntax used [? (Expression)]
@ : At symbol, signifies the current node being processed. Syntax used $.books[?(@.price > 100)]

Operator	Description
==	        left is equal to right (note that 1 is not equal to '1').
!=	        left is not equal to right.
<	        left is less than right.
<=	        left is less or equal to right.
>	        left is greater than right.
>=	        left is greater than or equal to right.
&&          combine predicates in AND
||          combine predicates in OR

"""


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
    Returns a list of items where variable exists
    """
    def _queryGetVariable(self, items, _variable: str):
        strQuery = "$[?"+_variable+"]"
        jpQuery = parse(strQuery)
        return [match.value for match in jpQuery.find(items)]

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

    def assertItemsCountNotEquals(self, items, count: int):
        _asserted = len(items) != count
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertItemsCountNotEquals.__name__, count])

    def assertEqual(self, items, var: str, val: str):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "=", val)
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertEqual.__name__, var, val])

    def assertEqual(self, items, var: str, val: int):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "=", str(val))
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertEqual.__name__, var, val])

    def assertNotEqual(self, items, var: str, val: str):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "!=", val)
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertNotEqual.__name__, var, val])

    def assertNotEqual(self, items, var: str, val: int):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "!=", str(val))
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertNotEqual.__name__, var, val])

    def assertGreaterThan(self, items, var: str, val: int):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, ">", str(val))
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertGreaterThan.__name__, var, val])

    def assertGreaterEqualThan(self, items, var: str, val: int):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, ">=", str(val))
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertGreaterEqualThan.__name__, var, val])

    def assertLesserThan(self, items, var: str, val: int):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "<", str(val))
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertLesserThan.__name__, var, val])

    def assertLesserEqualThan(self, items, var: str, val: int):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "<=", str(val))
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertLesserEqualThan.__name__, var, val])

    def assertNull(self, items, var: str):
        #totItems = len(items)
        matches = self._queryGetVariable(items, var)
        _asserted = len(matches) == 0
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertNull.__name__, var])

    def assertNotNull(self, items, var: str):
        totItems = len(items)
        matches = self._queryGetVariable(items, var)
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertNotNull.__name__, var])

    def assertTrue(self, items, var: str):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "=", "true")
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertTrue.__name__, var, "true"])

    def assertFalse(self, items, var: str):
        totItems = len(items)
        matches = self._queryGetMatchingRecords(items, var, "=", "false")
        _asserted = len(matches) == totItems
        if not _asserted:
            self.failures.append([ScenarioAsserter.assertFalse.__name__, var, "false"])
