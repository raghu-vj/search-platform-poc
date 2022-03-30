import json

with open("dumps/synonym_dump.json", 'r') as data:
    data_json = json.load(data)
    for obj in data_json:
        if 'input' in obj:
            print("\"" + obj['input'] + "," + ",".join(obj['synonyms']) + "\",")
        else:
            print("\"" + ",".join(obj['synonyms']) + "\",")