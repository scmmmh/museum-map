import json
import re
import spacy

from collections import Counter

from museum_map.models import ItemSchema

nlp = spacy.load('en')

with open('/home/mhall/Documents/Data/NML_Egypt/dataset.json') as in_f:
    schema = ItemSchema(include_data=('materials', 'images', 'owners', 'owners.person',
                                      'made_in', 'made_in.broader', 'made_in.broader.broader',
                                      'made_in.broader.broader.broader',
                                      'made_in.broader.broader.broader.broader',
                                      'made_in.broader.broader.broader.broader.broader',
                                      'made_in.broader.broader.broader.broader.broader.broader',
                                      'made_in.broader.broader.broader.broader.broader.broader.broader',
                                      'collected_in', 'collected_in.broader',
                                      'collected_in.broader.broader',
                                      'collected_in.broader.broader.broader',
                                      'collected_in.broader.broader.broader.broader',
                                      'collected_in.broader.broader.broader.broader.broader',
                                      'collected_in.broader.broader.broader.broader.broader.broader',
                                      'collected_in.broader.broader.broader.broader.broader.broader.broader'))
    raw = json.load(in_f)
    data = schema.load(raw, many=True)


def extract_dynasty(date):
    match = re.search('Dynasty ([0-9]{1,2})(?: BC)? - (?:Dynasty )?([0-9]{1,2})(?: BC)?', date)
    if match:
        return list(range(int(match.group(1)), int(match.group(2)) + 1))
    match = re.search('Dynasty ([0-9]{1,2})', date)
    if match:
        return [int(match.group(1))]
    return None

for obj in data.data:
    dynasty = extract_dynasty(obj['date_made'])
    if dynasty:
        obj['dynasty'] = tuple(dynasty)
    else:
        obj['dynasty'] = None
    #print(nlp(obj['title']))
    #print(obj.keys())

keys = [('id', None),
        ('maker', None),
        ('materials', 'term'),
        ('category', None),
        ('measurements', None),
        ('place_made', None),
        ('culture', None),
        ('date_made', None),
        ('made_in', 'name'),
        ('dynasty', None)]
for key, access in keys:
    tmp = []
    for obj in data.data:
        if isinstance(obj[key], list):
            for x in obj[key]:
                if x:
                    if access:
                        tmp.append(x[access])
                    else:
                        tmp.append(x)
        elif obj[key]:
            tmp.append(obj[key])
    counter = Counter(tmp)
    ids = set()
    for value, _ in counter.most_common(10):
        for obj in data.data:
            if isinstance(obj[key], list):
                for x in obj[key]:
                    if x:
                        if access and x[access] == value:
                            ids.add(obj['id'])
                        elif x == value:
                            ids.add(obj['id'])
            elif obj[key] and obj[key] == value:
                ids.add(obj['id'])
    print(key, len(counter), len(ids) / len(data.data))
