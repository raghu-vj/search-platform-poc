import requests, json
import csv
import re

import config


def convert_rule_to_template(anchor,consequence):
        # print consequence['params']['optionalFilters']
        final_list = []
        for cons in consequence['params']['optionalFilters']:
            # print cons
            data = {}
            match = {}
            cons_str = str(cons)

            consequence_reg = re.search('(.*):(.*)<score=(.*)>', cons_str)

            match_field = consequence_reg.group(1)
            match_field_value = consequence_reg.group(2)
            score = consequence_reg.group(3)

            normalised_score = ((float)(score)/100.0) + 1.0

            if(match_field.find(".") == -1):
                final_list.append(get_key_word_type_query_json(match_field,match_field_value,normalised_score))
            else:
                final_list.append(get_nested_type_query_json(match_field,match_field_value,normalised_score))


            # json_data = json.dumps(data)
            # final_list.append(data)

        # final_data = {}
        # final_data['should'] = final_list
        return final_list



def get_key_word_type_query_json(match_field,match_field_value,score):
        data = {}
        match = {}
        match_data = {}
        match_data['query'] = match_field_value
        match_data['boost'] = score

        match[match_field] = match_data
        data['match'] = match
        # print(match_field_value)
        # print(score)
        return data


def get_nested_type_query_json(match_field,match_field_value,score):
        data = {}
        match = {}
        query = {}
        nested = {}
        match[match_field + '.exahaustive'] = match_field_value

        query['match'] = match

        nested['query'] = query
        nested['path'] = match_field.split('.',1)[0]
        nested['boost'] = score

        data['nested'] = nested
        # print(match_field_value)
        # print(score)
        return data




def get_templatised_rule_data(query):
    with open('rules_v1.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else:
                anchoring = row[4]
                pattern = str(row[5])
#                 print('anchoring: {} , pattern: {} and query: {}'.format(anchoring,pattern,query))
                if (row[1] == 'TRUE' and ((anchoring == 'is' and pattern.strip().lower() == query) or (anchoring == 'contains' and query.find(pattern.strip().lower()) != -1 ))):
                    consequence_json = row[8]
#                     print consequence_json
                    consequence = json.loads(consequence_json)
                    return convert_rule_to_template(anchoring,consequence)
            line_count += 1
#             print(' anchoring: {} , consequence  {} '.format(anchoring,consequence))
#         print('Processed {} lines.'.format(line_count))
        return []


def get_alternate_words_for_query(query):
    with open('data/alternate_words.csv') as csv_file:
         csv_reader = csv.reader(csv_file, delimiter=',')
         line_count = 0
         final_list = [query]
         for row in csv_reader:
            if query in row:
                row.remove(query)
                final_list = final_list + row
         return final_list



def get_es_request_for_query(query):
    query = str(query).strip().lower()
    data = {}
    data['id'] = config.ES_TEMPLATE_NAME
    params = {}
    params['query'] = query
    alternate_queries = get_alternate_words_for_query(query)
#     print(alternate_queries)
    for q in alternate_queries:
        template_converted_rule_list = get_templatised_rule_data(q)
        if(len(template_converted_rule_list) > 0):
            break
    if len(template_converted_rule_list) > 0:
        params['rules'] = template_converted_rule_list
    data['params'] = params
    return json.dumps(data)