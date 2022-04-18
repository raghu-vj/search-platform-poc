import json


def test():
    alternate_spellings = []
    for line in open("es_index/alternate_spellings.txt", "r").readlines():
        alternate_spellings.append(line.strip())
    multiword_synonyms = []
    for line in open("es_index/multi_word_synonyms.txt", "r").readlines():
        multiword_synonyms.append(line.strip())
    with open("es_index/settings_mappings_v0.json", 'r') as data:
        read = data.read()
        print(read)
        json_data = json.loads(read)
        json_data['settings']['index']['analysis']['filter']['alternate_spelling_filter']['synonyms'] = alternate_spellings
        json_data['settings']['index']['analysis']['filter']['typo_filter'][
            'synonyms'] = alternate_spellings
        json_data['settings']['index']['analysis']['filter']['synonym_filter'][
            'synonyms'] = multiword_synonyms
        json_data['settings']['index']['analysis']['filter']['graph_synonyms'][
            'synonyms'] = multiword_synonyms
        json_data_str = json.dumps(json_data)
        print(json_data_str)


test()