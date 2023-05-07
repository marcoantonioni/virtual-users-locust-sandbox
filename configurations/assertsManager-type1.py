import json, logging

from jsonpath_ng.ext import parse

# ./outputdata/unittest-scenario1.json

#---------------------------------------------------------
# https://scrapfly.io/blog/parse-json-jsonpath-python/

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

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

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


"""
#---------------------------------------------------------

def exampleGetVariablesFromAllCompleted(listOfInstances):
    strQuery = "$[?(@.state=='Completed')].variables"
    print(strQuery)
    jpQuery = parse(strQuery)
    matches = [match.value for match in jpQuery.find(listOfInstances)]
    for match in matches:
        print("exampleGetVariablesFromAllCompleted", match)

def exampleGetVariablesFromAllCounterLessThan(listOfInstances, threshold: int):
    # simplified without (@.
    strQuery = "$[?variables.inputData.newCounter <= " + str(threshold) + "].variables"
    #strQuery = "$[?(@.variables.inputData.newCounter <= " + str(threshold) + ")].variables"
    print(strQuery)
    jpQuery = parse(strQuery)
    matches = [match.value for match in jpQuery.find(listOfInstances)]
    for match in matches:
        print("exampleGetVariablesFromAllCounterLessThan", match)

def exampleGetVariablesFromAllCompletedAndCounterLessThan(listOfInstances, threshold: int):
    strQuery = "$[?(@.state=='Completed' & @.variables.inputData.newCounter <= " + str(threshold) + " )].variables"
    print(strQuery)
    jpQuery = parse(strQuery)
    matches = [match.value for match in jpQuery.find(listOfInstances)]
    for match in matches:
        print("exampleGetVariablesFromAllCompletedAndCounterLessThan", match)

def executeAsserts(listOfInstances):
    print("======> executeAsserts")
    print(json.dumps(listOfInstances, indent=2))

    exampleGetVariablesFromAllCompleted(listOfInstances)
    exampleGetVariablesFromAllCounterLessThan(listOfInstances, 50)
    exampleGetVariablesFromAllCompletedAndCounterLessThan(listOfInstances, 200)

"""
with open('./outputdata/unittest-scenario1-bis.json') as f:
    d = json.load(f)
    # print(json.dumps(d, indent=2))

    jeState = parse('$[*].DATA.state')
    jeAuthData = parse('$[*].DATA.variables.authorizationData')    

    jeCounter = parse("$[?(@.DATA.variables.inputData.newCounter < 70)].PID")
    
    for match in jeState.find(d):
        print(f'state: {match.value}')

    print()
    for match in jeAuthData.find(d):
        print(f'authData: {match.value}')

    print()
    for match in jeCounter.find(d):
        print(f'counter: {match.value}')
"""


"""
with open('/home/marco/locust/studio/virtual-users-locust-sandbox/outputdata/movies.json') as movies_json:
	movies = json.load(movies_json)
	
# query = "$.movies[?(@.cast[:] =~ 'De Niro')].title"
query = "$[?(@.year < 1995)].title"

jsonpath_expression = parse(query)

for match in jsonpath_expression.find(movies):
    print(match.value)
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
print(matches)

"""