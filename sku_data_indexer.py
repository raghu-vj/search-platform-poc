import json

import requests

base_es_host = "https://search-search-perf-public-sfhpf2qga7guxicrs322krkrl4.ap-southeast-1.es.amazonaws.com"
index_name = "sku_data_instamart_store_788741"
url = "%s/%s" % (base_es_host, index_name)
bulk_write_url = url + "/_bulk"
batch_size = 250

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
    with open("es_index/settings_mappings_v0.json", 'r') as data:
        response = requests.request("PUT", url, headers=headers, data=data)
        print("index creation response" + response.text)

def index_data():
    write_dict = {'create': {'_id': '0', '_index': index_name, 'retry_on_conflict': 2}}
    request_body = ""
    with open("dumps/instamart_store_788741.json", 'r') as data:
        data_json = list(json.load(data))
        for i in range(0, len(data_json), batch_size):
            chunk = data_json[i:i + batch_size]
            for obj in chunk:
                write_dict['create']['_id'] = obj['id']
                request_body = request_body + json.dumps(write_dict) + "\n"
                request_body = request_body + json.dumps(obj) + "\n"
            print(request_body)
            response = requests.request("POST", bulk_write_url, headers=headers, data=request_body)
            print(response.status_code)


if __name__ == "__main__":
    create_index()
    index_data()

