import requests, json
import csv
import re

import config


def convert_rule_to_template(anchor, consequence, is_query_exact_matching_with_rule_queries):
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

            if is_query_exact_matching_with_rule_queries:
                normalised_score = ((float)(score) / 1.0)
            else:
                normalised_score = ((float)(score) / 1000.0)

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
        match[match_field + '.exhaustive'] = match_field_value

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
        template_section = []
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
                continue
            else:
                anchoring = row[4]
                pattern = str(row[5])
#                 print('anchoring: {} , pattern: {} and query: {}'.format(anchoring,pattern,query))
                is_rule_satisfied, is_query_exact_matching_with_rule_queries = is_rule_condition_satisfied(query, pattern, anchoring, row[1])
                if is_rule_satisfied:
                    consequence_json = row[8]
#                     print consequence_json
                    consequence = json.loads(consequence_json)
                    template_section = convert_rule_to_template(anchoring, consequence,
                                                        is_query_exact_matching_with_rule_queries)

                if is_rule_satisfied and is_query_exact_matching_with_rule_queries:
                    consequence_json = row[8]
                    #                     print consequence_json
                    consequence = json.loads(consequence_json)
                    template_section = convert_rule_to_template(anchoring, consequence,
                                                                is_query_exact_matching_with_rule_queries)
                    return template_section

            line_count += 1
#             print(' anchoring: {} , consequence  {} '.format(anchoring,consequence))
#         print('Processed {} lines.'.format(line_count))
        return template_section


def is_rule_condition_satisfied(query,pattern,anchoring,active):
    if(active != 'TRUE'):
        return False, False

    is_one_edit_distance_true, is_same_str = is_edit_distance_one_or_less(pattern.strip().lower(), query)
    if is_same_str and len(query) >= 3:
        return True, True
    if is_one_edit_distance_true and len(query) >= 3:
        return True, False

    if(anchoring == 'contains' and query.find(pattern.strip().lower()) != -1 ) and len(query) - len(pattern) <= 2:
        return True, False
    return False, False


def is_edit_distance_one_or_less(s1, s2):
    m = len(s1)
    n = len(s2)
    if(s1 == s2):
        return True, True
    if abs(m - n) > 1:
        return False, False
    count = 0
    i = 0
    j = 0
    while i < m and j < n:
        if s1[i] != s2[j]:
            if count == 1:
                return False, False
            if m > n:
                i+=1
            elif m < n:
                j+=1
            else:
                i+=1
                j+=1
            count+=1
        else:
            i+=1
            j+=1
    if i < m or j < n:
        count+=1

    return count == 1, False

def get_alternate_words_for_query(query):
    with open('es_index/alternate_spellings.txt') as csv_file:
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