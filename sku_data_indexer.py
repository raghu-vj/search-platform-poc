import json

import requests

import config

url = "%s/%s" % (config.BASE_ES_HOST, config.INDEX_NAME)
bulk_write_url = url + "/_bulk"
batch_size = 800

headers = {
    'User-Agent': '-t',
    'Content-Type': 'application/json'
}


def get_indexable_doc(obj):
    doc = {}
    doc['category'] = {}
    doc['category']['name'] = obj['category']['name']
    doc['category']['id'] = obj['category']['id']
    doc['category']['description'] = obj['category']['description']
    # attributes
    attrs = {}
    attrs['type'] = obj['attributes'].get('type', None)
    attrs['product_name'] = obj['attributes'].get('product name', None)
    attrs['brand'] = obj['attributes'].get('brand', None)
    attrs['model_name'] = obj['attributes'].get('model_name', None)
    attrs['pack_type'] = obj['attributes'].get('pack_type', None)
    attrs['sub_category/L3'] = obj['attributes'].get('sub-category/L3', None)
    attrs['category/I2'] = obj['attributes'].get('category/l2', None)
    attrs['category/L2'] = obj['attributes'].get('category/L2', None)
    attrs['super_category/L1'] = obj['attributes'].get('super_category/L1', None)
    attrs['super_category/I1'] = obj['attributes'].get('super category/l1', None)
    attrs['sub_category/I1'] = obj['attributes'].get('sub-category/l1', None)
    attrs['pack_type'] = obj['attributes'].get('pack_type', None)
    attrs['form_factor'] = obj['attributes'].get('form_factor', None)
    doc['attributes'] = attrs
    doc['spin'] = obj['spin']
    return doc


def create_index():
    delete_res = requests.request("DELETE", url, headers=headers)
    print("Deleting existing index, response: " + delete_res.text)
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
        response = requests.request("PUT", url, headers=headers, data=json_data_str)
        print("index creation response" + response.text)

def index_data():
    write_dict = {'create': {'_id': '0', '_index': config.INDEX_NAME, 'retry_on_conflict': 2}}
    request_body = ""
    with open("dumps/instamart_store_%s.json" % config.STORE_ID, 'r') as data:
        data_json = list(json.load(data))
        for i in range(0, len(data_json), batch_size):
            chunk = data_json[i:i + batch_size]
            for obj in chunk:
                write_dict['create']['_id'] = obj['id']
                request_body = request_body + json.dumps(write_dict) + "\n"
                request_body = request_body + json.dumps(get_indexable_doc(obj)) + "\n"
            print(request_body)
            response = requests.request("POST", bulk_write_url, headers=headers, data=request_body)
            print(response.status_code)


if __name__ == "__main__":
    create_index()
    index_data()

