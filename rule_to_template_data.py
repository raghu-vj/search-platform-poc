import csv
import json
import re


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

            if(match_field.find(".") == -1):
                final_list.append(get_key_word_type_query_json(match_field,match_field_value,score))
            else:
                final_list.append(get_nested_type_query_json(match_field,match_field_value,score))


            # json_data = json.dumps(data)
            # final_list.append(data)

        # final_data = {}
        # final_data['should'] = final_list
        return final_list
#         final_data_json = json.dumps(final_list)
#         print('final list for multi_match rule conversion')
#         print(final_data_json)
#         return final_data_json



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
                # print('Column names are:{}, {}'.format(row[4], row[5]))
                pass
            else:
                anchoring = row[4]
                pattern = row[5]
                # print('anchoring: {} , pattern: {} and query: {}'.format(anchoring,pattern,query))
                if (row[1] == 'TRUE' and ((anchoring == 'is' and pattern == query) or (anchoring == 'contains' and query.find(pattern) != -1 ))):
                    consequence_json = row[8]
                    # print(consequence_json)
                    consequence = json.loads(consequence_json)
                    return convert_rule_to_template(anchoring,consequence)
            line_count += 1
                # print(' anchoring: {} , consequence  {} '.format(anchoring,consequence))
        # print('Processed {} lines.'.format(line_count))
        return []


def get_es_request_for_query(query):
    data = {}
    data['id'] = 'sku_insta_search_v0'

    params = {}
    params['query'] = query

    template_converted_rule_list = get_templatised_rule_data(query)
    if len(template_converted_rule_list) > 0:
        params['rules'] = template_converted_rule_list

    data['params'] = params
    return json.dumps(data)





