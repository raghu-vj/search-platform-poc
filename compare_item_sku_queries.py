import json
import os

import requests
from scipy.stats import kendalltau

import config
import item_sku_dump
from rule_to_template_data import get_es_request_for_query

def levenshtein(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    current = range(n + 1)
    for i in range(1, m + 1):
        previous, current = current, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete = previous[j] + 1, current[j - 1] + 1
            change = previous[j - 1]
            if a[j - 1] != b[i - 1]:
                change = change + 1
            current[j] = min(add, delete, change)

    return current[n]

def get_dashservice_response(query):
    url = "http://localhost:8080/api/dash/search/menu"
    payload = "{\n    \"storeId\": \"" + config.STORE_ID + "\",\n    \"query\": \"" + query + "\",\n    \"userId\" : \"123\",\n    \"cityId\" : 1,\n    \"searchSource\": \"ALGOLIA\"\n}"
    headers = {
        'Content-Type': 'application/json',
        'swuid': 'raghu_swuid',
        'requestId': 'raghu_rid'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = json.loads(response.text)
    final_names_list = []
    for info in json_data['data']['productInfos']:
        final_names_list.append(item_sku_dump.get_product_name_from_id(info['productId'])['attributes']['product name'])
    with open("dumps/queries/" + query + "/algolia.txt", "w") as f:
        for name in final_names_list:
            f.write("%s\n" % name)
    return final_names_list


def get_es_response(query):
        url = "%s/%s/_search/template" % (config.BASE_ES_HOST, config.INDEX_NAME)
        headers = {
            'Content-Type': 'application/json'
        }
        es_query = get_es_request_for_query(query)
        response = requests.request("POST", url, headers=headers, data=es_query)
        json_data = json.loads(response.text)

        final_names_list = []
        if 'hits' in json_data and 'hits' in json_data['hits']:
            for hit in json_data['hits']['hits']:
                final_names_list.append(hit['_source']['attributes']['product_name'])
            with open("dumps/queries/" + query + "/es.txt", "w") as f:
                for name in final_names_list:
                    f.write("%s\n" % name)
        return final_names_list


def read_from_dumped_file(query):
    list = []
    f = open("dumps/queries/" + query + "/algolia.txt", 'r')
    for line in f.readlines():
        list.append(line)
    return list


def compare():
    queries = os.listdir("dumps/queries")
#     queries = ['apple']
    print("QUERY,algolia-recall-length,es-recall-length,levenstein-distance,kendalltau,recall-similarity,recall-similarity %,recall-absent")
    for query in queries:
        get_dashservice_response(query)
        get_es_response(query)
        dash_file = "dumps/queries/" + query + "/algolia.txt"
        es_file = "dumps/queries/" + query + "/es.txt"

        # FILE reading
        # build es list
        es_list = []
        es_file_obj = open(es_file, "r")
        for line in es_file_obj.readlines():
            es_list.append(line)

        # FILE reading
        # build algolia list
        algolia_list = []
        algolia_file_obj = open(dash_file, "r")
        for line in algolia_file_obj.readlines():
            algolia_list.append(line)

        # recall_similar_list = set(algolia_list) & set(es_list)
        recall_similar_list = [x for x in algolia_list if x in es_list]
        # os.system("diff -y " + dash_file + " " + es_file)
        recall_absent_list = [x for x in algolia_list if x not in es_list]
        corr, _ = kendalltau(algolia_list[:len(recall_similar_list)], recall_similar_list)
        print(query + ", " + str(len(algolia_list)) + ", " + str(len(es_list)) + ", " + str(levenshtein(algolia_list, es_list)) + ", " + str(corr) + ", " + str(len(recall_similar_list)) + ", " + str(len(recall_similar_list) * 100 / len(algolia_list)) + ", " + str("|".join(str(x.strip()) for x in recall_absent_list)))


if __name__ == '__main__':
    compare()
