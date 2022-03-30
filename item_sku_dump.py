import json
from algoliasearch.search_client import SearchClient

client = SearchClient.create('YTD9R9DRZL', '30a63e134c9f98def99e299a73e5a2c5')
index = client.init_index('sku_data')


def hit_algolia_and_dump_file():
    hits = []
    # store_id: 810366 : andheri mumbai
    algolia_result = index.browse_objects({'filters': 'store_id:810366'})
    count = 0
    for hit in algolia_result:
        hits.append(hit)
        count = count + 1
        print(hit)
    print(count)
    with open('/Users/mayank.solanki/Documents/workspace/search-platform-poc/dumps/instamart_store_810366.json', 'w') as f:
        json.dump(hits, f)


def get_product_name_from_id_list(idList):
    final_map = {}
    for id in idList:
        final_map[id] = get_product_name_from_id(id)
    return final_map

def get_product_name_from_id(id):
    filter_query = "store_id:810366 AND attributes.product_id:" + id
    algolia_result = index.browse_objects({'filters': filter_query})
    for hit in algolia_result:
        return hit


if __name__ == "__main__":
    print 'hello'
    hit_algolia_and_dump_file()
