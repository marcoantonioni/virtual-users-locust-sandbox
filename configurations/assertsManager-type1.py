import json, logging
#from jsonpath_ng import jsonpath, parse
from jsonpath_ng.ext import parse

# ./outputdata/unittest-scenario1-bis.json

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