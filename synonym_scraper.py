import json

with open("dumps/synomym_dump_v1.json", 'r') as data:
    data_json = json.load(data)
    for obj in data_json:
        if 'input' in obj:
            print(obj['input'] + "," + ",".join(obj['synonyms']).lower() + ",")
        else:
            print(",".join(obj['synonyms']).lower() + ",")