import json


def read_from_file(file_name):
    with open(file_name, "r") as file:
        return file.read()


def append_to_file(file, text):
    file.write(text)
    file.write("\n")


def println(list):
    print(','.join(list))


if __name__ == '__main__':
    file = open("generated/algolia_replace_rule_alternate_spellings.txt", "a")
    lines = read_from_file("data/algolia_replace_rules.txt").split("\n")
    print "Error rules: "
    for line in lines:
        try:
            rule_json = json.loads(line)
            alternate_spellings = set()
            for edit in rule_json['params']['query']['edits']:
                alternate_spellings.add(edit['delete'])
                alternate_spellings.add(edit['insert'])
            append_to_file(file, ','.join(alternate_spellings))
        except:
            print(line)
    file.close()