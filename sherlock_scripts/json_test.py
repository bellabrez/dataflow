import json

mydict = {'gender': 'female',
          'age': 7,
          'genotype': '99/1_GCaMP6f',
          'circadian_on': 1,
          'circadian_on'}

with open('result.json', 'w') as fp:
    json.dump(mydict, fp, indent=4)