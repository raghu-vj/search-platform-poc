import json
from algoliasearch.search_client import SearchClient
import config

client = SearchClient.create('YTD9R9DRZL', '30a63e134c9f98def99e299a73e5a2c5')
index = client.init_index('sku_data')


def hit_algolia_and_dump_file():
    hits = []
    # store_id: 788741
    algolia_result = index.browse_objects({'filters': 'store_id:788741'})
    count = 0
    for hit in algolia_result:
        hits.append(hit)
        count = count + 1
        print(hit)
    print(count)
    with open('dumps/instamart_store_788741.json', 'w') as f:
        json.dump(hits, f)


def get_product_name_from_id_list(idList):
    final_map = {}
    for id in idList:
        final_map[id] = get_product_name_from_id(id)
    return final_map

def get_product_name_from_id(id):
    filter_query = "store_id:%s AND attributes.product_id:" % (config.STORE_ID) + id
    algolia_result = index.browse_objects({'filters': filter_query})
    for hit in algolia_result:
        return hit


def dump_synonyms():
    json_list = []
    for synonym in index.browse_synonyms():
        load = json.loads(json.dumps(synonym))
        json_list.append(load)
    print(json.dumps(json_list))


if __name__ == "__main__":
    hit_algolia_and_dump_file()
    # dump_synonyms()
