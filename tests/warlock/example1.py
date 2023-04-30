import warlock
import json

MySchema1 = {
    'name': 'Country',
    'properties': {
        'name': {'type': 'string'},
        'abbreviation': {'type': 'string'},
        'population': {'type': 'integer'},
        'variables': {'type': 'object'}
    },
    'additionalProperties': False,
}

Country = warlock.model_factory(MySchema1)

sweden = Country(name='Sweden', abbreviation='SE')

print(json.dumps(sweden))

sweden.population = 10

print(json.dumps(sweden))

sweden.variables = { 'person': { 'name':'ugo', 'age':5}, 'contract':{'type':'Normal','value':1234} }

print(json.dumps(sweden))

# force error
# sweden.population = 'none'

data = '{"name": "Italy", "abbreviation": "IT", "population": 1000, "variables": {"person": {"name": "ugo", "age": 5}, "contract": {"type": "Normal", "value": 1234}}}'
italy = Country(json.loads(data))
print(json.dumps(italy))

data2 = {"name": "Italy2", "abbreviation": "IT", "population": 100000, "variables": {"person": {"name": "ugo", "age": 5}, "contract": {"type": "Normal", "value": 1234}}}
italy2 = Country(data2)
print(json.dumps(italy2))


print(italy2["name"])
print(italy2["variables"]["person"])
print(italy2["variables"]["person"]["age"])
print(italy2["variables"]["contract"])


