import json
import os
from multiprocessing import Process

import requests
from paramiko.client import SSHClient
from scipy.stats import kendalltau

import config
import item_sku_dump
from rule_to_template_data import get_es_request_for_query

client = SSHClient()
client.load_system_host_keys()
client.connect('sp.swiggy.co', port=4242, username=config.SSH_USER_NAME)
SEPARATOR = "\t"

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


def curl_request(url,method,headers,payloads):
    # construct the curl command from request
    command = "curl -v -H {headers} {data} -X {method} {uri}"
    data = " -d '" + payloads + "'"
    header_list = ['"{0}: {1}"'.format(k, v) for k, v in headers.items()]
    header = " -H ".join(header_list)
    return command.format(method=method, headers=header, data=data, uri=url)


def get_dashservice_response(query):
    url = "http://dash-search.production.singapore/api/dash/search/menu"
    payload = "{\n    \"storeId\": \"" + config.STORE_ID + "\",\n    \"query\": \"" + query + "\",\n    \"userId\" : \"123\",\n    \"cityId\" : 1,\n    \"searchSource\": \"ALGOLIA\"\n}"
    headers = {
        'Content-Type': 'application/json',
        'swuid': 'raghu_swuid',
        'requestId': 'raghu_rid'
    }
    # response = requests.request("POST", url, headers=headers, data=payload)
    request = curl_request(url, "POST", headers, payload)
    _, stdout, _ = client.exec_command(request)
    json_data = json.loads(stdout.read())
    final_names_list = []
    for info in json_data['data']['productInfos']:
        final_names_list.append(item_sku_dump.get_product_name_from_id(info['productId'])['attributes']['product name'])
    with open("dumps/queries/" + query + "/algolia.txt", "w") as f:
        for name in final_names_list:
            f.write("%s\n" % name)
    return final_names_list


def get_es_response(query, print_query):
        url = "%s/%s/_search/template" % (config.BASE_ES_HOST, config.INDEX_NAME)
        headers = {
            'Content-Type': 'application/json'
        }
        es_query = get_es_request_for_query(query)
        if print_query:
            print("ES query: " + es_query)
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
    queries = open("data/low_recall_queries.txt", "r").read().split("\n")
    # queries = ['dai']
    print("QUERY\talgolia-recall-length\tes-recall-length\tlevenstein-distance\tkendalltau\trecall-similarity\trecall-similarity %\trecall-absent")
    no_of_queries = len(queries)
    print_es_query = no_of_queries == 1
    processes = list()

    for query in queries:
        p = Process(compare_given_query(query, print_es_query))
        p.start()
        processes.append(p)

    for pro in processes:
        pro.join()

def compare_given_query(query, print_es_query):
    folder = "dumps/queries/" + query
    if not os.path.exists(folder):
        os.makedirs(folder)
    # get responses
    get_dashservice_response(query)
    get_es_response(query, print_es_query)
    dash_file = folder + "/algolia.txt"
    es_file = folder + "/es.txt"
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
    print(query + SEPARATOR + str(len(algolia_list)) + SEPARATOR + str(len(es_list)) + SEPARATOR + str(
        levenshtein(algolia_list, es_list)) + SEPARATOR + str(corr) + SEPARATOR + str(
        len(recall_similar_list)) + SEPARATOR + str(
        len(recall_similar_list) * 100 / len(algolia_list)) + SEPARATOR + str(
        "|".join(str(x.strip()) for x in recall_absent_list)))


if __name__ == '__main__':
    compare()
