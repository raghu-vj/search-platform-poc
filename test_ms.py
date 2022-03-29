import json
import requests
import sys
from rule_to_template_data import get_es_request_for_query


QUERY = str(sys.argv[1])

url = "https://search-search-perf-public-sfhpf2qga7guxicrs322krkrl4.ap-southeast-1.es.amazonaws.com/sku_data_v6/_search"
headers = {
    'Content-Type': 'application/json'
}
#         es_query = f.read().replace("$query$", query)
es_query = get_es_request_for_query(QUERY)
print('query sent to es with rules: {}'.format(es_query))
# response = requests.request("POST", url, headers=headers, data=es_query)
# json_data = json.loads(response.text)
# final_names_list = []
# for hit in json_data['hits']['hits']:
#     final_names_list.append(hit['_source']['attributes']['product_name'])
# print('final product: {}'.format(final_names_list))