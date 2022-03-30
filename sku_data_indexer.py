import json

import requests

url = "https://search-search-perf-public-sfhpf2qga7guxicrs322krkrl4.ap-southeast-1.es.amazonaws.com/sku_data_v7"
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


with open("/Users/mayank.solanki/Documents/workspace/search-platform-poc/dumps/instamart_store_810366.json", 'r') as data:
    data_json = json.load(data)
    for obj in data_json:
        doc = get_indexable_doc(obj)
        print(doc)
        response = requests.request("POST", url + "/_doc/" + obj['id'], headers=headers, data=json.dumps(doc))
        print(response.status_code)