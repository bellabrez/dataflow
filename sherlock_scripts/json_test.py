import json

mydict = {'gender': 'female',
          'age': 7,
          'genotype': '99/1_GCaMP6f',
          'circadian_on': 1,
          'circadian_off': 13,
          'temp': 25,
          'notes': ''}

mylist = [{'name': 'SineGrating', 'angle': 90, 'period': 40, 'rate': 100, 'color': 1},
{'name': 'SineGrating', 'angle': 0, 'period': 40, 'rate': 100, 'color': 1},
{'name': 'SineGrating', 'angle': 270, 'period': 40, 'rate': 100, 'color': 1},
{'name': 'SineGrating', 'angle': 180, 'period': 40, 'rate': 100, 'color': 1}]

with open('result.json', 'w') as fp:
    json.dump(mylist, fp, indent=4)

with open('result.json', 'w') as fp:
    json.dump(mylist, fp, indent=4)