import itertools
import json
import re
import spacy

from collections import Counter

from museum_map.models import ItemSchema

nlp = spacy.load('en')

with open('/home/hall/Documents/Data/NML_Egypt/dataset.json') as in_f:
    data = in_f.read()

with open('/home/hall/Documents/Data/NML_Egypt/dataset.json', 'w') as out_f:
    data = data.replace('Hyksos or New Kingdom', 'Hyksos - New Kingdom')
    out_f.write(data)


print('Loading')

with open('/home/hall/Documents/Data/NML_Egypt/dataset.json') as in_f:
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

print('Extracting Dynasties')

for obj in data.data:
    dynasty = extract_dynasty(obj['date_made'])
    if dynasty:
        obj['dynasty'] = tuple(dynasty)
    else:
        obj['dynasty'] = None
    #print(nlp(obj['title']))
    #print(obj.keys())

KEYS = [('maker', None),
        ('materials', 'term'),
        ('category', None),
        #('measurements', None),
        ('place_made', None),
        ('culture', None),
        #('date_made', None),
        ('made_in', 'name'),
        ('dynasty', None)]


def filter_data(data, filters):
    result = []
    for obj in data:
        do_filter = False
        for (key, access), value in filters:
            if isinstance(obj[key], list):
                for x in obj[key]:
                    if x:
                        if access:
                            if x[access] == value:
                                do_filter = True
                        elif x == value:
                            do_filter = True
            elif obj[key] == value:
                do_filter = True
            if do_filter:
                break
        if do_filter:
            result.append(obj)
    return result


def best_effort_bins(values, target_bin_count):
    target = int(sum([v[1] for v in values]) / target_bin_count)
    bins = [{'values': [], 'total': 0} for _ in range(0, target_bin_count)]
    for value, count in values:
        binned = False
        for idx in range(0, target_bin_count):
            if bins[idx]['total'] + count <= target:
                bins[idx]['values'].append(value)
                bins[idx]['total'] = bins[idx]['total'] + count
                binned = True
                break
        if not binned:
            min_bin = None
            min_value = 0
            for idx in range(0, target_bin_count):
                if min_bin is None or bins[idx]['total'] + count - target < min_value:
                    min_bin = idx
                    min_value = bins[idx]['total'] + count - target
            bins[min_bin]['values'].append(value)
            bins[min_bin]['total'] = bins[idx]['total'] + count
    return bins


def dynasty_ordering(value):
    if isinstance(value, dict):
        return value['values'][0]
    else:
        return value


def culture_ordering(value):
    if isinstance(value, dict):
        value = value['values'][0]
    return ['Predynastic ?',
            'Predynastic Period (Naqada I)',
            'Predyndastic Period (Naqada II) or Early Dynastic Period',
            'Predynastic Period (Naqada II)',
            'Early Dynastic - early Old Kingdom',
            'Old Kingdom',
            'First Intermediate Period',
            'First Intermediate Period - Middle Kingdom',
            'Middle Kingdom',
            'Middle Kingdom - Second Intermediate Period',
            'Middle Kingdom or New Kingdom',
            'Middle Kingdom or later',
            'Hyksos',
            'Hyksos - New Kingdom',
            'Second Intermediate Period',
            'Second Intermediate Period - Hyksos',
            'Second Intermediate Period - Early New Kingdom',
            'Second Intermediate Period - New Kingdom',
            'Early New Kingdom',
            'New Kingdom',
            'New Kingdom (Ramesside Period)',
            'New Kingdom (Ramesside Period) - Third Intermediate Period',
            'New Kingdom - Late Period',
            'Third Intermediate Period',
            'Third Intermediate Period - Late Period',
            'Late Period',
            'Late Period (Saite)',
            'Late Period or later',
            'Late Period/Phoenician or Ptolemaic',
            'Late Period - Romano-Egyptian',
            'Ptolemaic',
            'Roman Period'].index(value)


def ordered_bins(values, target_size, ordering, single_value=True):
    bins = set()
    for value, _ in values:
        if single_value:
            bins.add(value)
        else:
            for v in value:
                bins.add(v)
    bins = list(bins)
    bins = dict([(b, 0) for b in bins])
    for value, counts in values:
        if single_value:
            bins[value] = counts
        else:
            for v in value:
                bins[v] = bins[v] + counts
    bins = [{'values': [k], 'total': v} for k, v in bins.items()]
    bins.sort(key=ordering)
    while len(bins) > 1:
        merged = False
        for idx in range(0, len(bins) - 1):
            if bins[idx]['total'] + bins[idx + 1]['total'] <= target_size:
                for v in bins[idx + 1]['values']:
                    if v not in bins[idx]['values']:
                        bins[idx]['values'].append(v)
                bins[idx]['total'] = bins[idx + 1]['total']
                del bins[idx + 1]
                merged = True
                break
        if not merged:
            break
    return bins


def split_data(data, filter_keys=[], indent=0):
    #data = filter_data(data, filters)
    keys = [k for k in KEYS if k[0] not in filter_keys]
    if len(data) <= 50 or len(keys) == 0:
        return  # TODO: actual processing
    best = (0.0, 10000)
    best_key = None
    best_values = None
    for key, access in keys:
        # Determine all values for key
        tmp = []
        for obj in data:
            if isinstance(obj[key], list):
                for x in obj[key]:
                    if x:
                        if access:
                            tmp.append(x[access])
                        else:
                            tmp.append(x)
            elif obj[key]:
                tmp.append(obj[key])
        # Count the values
        counter = Counter(tmp)
        ids = set()
        for value, _ in counter.most_common():
            for obj in data:
                if isinstance(obj[key], list):
                    for x in obj[key]:
                        if x:
                            if access and x[access] == value:
                                ids.add(obj['id'])
                            elif x == value:
                                ids.add(obj['id'])
                elif obj[key] and obj[key] == value:
                    ids.add(obj['id'])
        if len(ids) / len(data) > best[0] or (len(ids) / len(data) > best[0] and len(counter) < best[1]):
            best = (len(ids) / len(data), len(counter))
            best_key = (key, access)
            best_values = counter.most_common()
    # These need to be binned into at most 10 bins, to aim for a room size of about 20 items
    if best_key[0] == 'dynasty':
        bins = ordered_bins(best_values, round(sum([v[1] for v in best_values]) / min(10, int(len(data) / 20))), dynasty_ordering, False)
    elif best_key[0] == 'culture':
        bins = ordered_bins(best_values, round(sum([v[1] for v in best_values]) / min(10, int(len(data) / 20))), culture_ordering)
    else:
        bins = best_effort_bins(best_values, min(10, int(len(data) / 20)))
    for data_bin in bins:
        if data_bin['total'] > 0:
            filtered_data = filter_data(data, [(best_key, v) for v in data_bin['values']])
            if best_key[0] == 'dynasty':
                labels = data_bin['values']
                labels.sort(key=dynasty_ordering)
                labels = [str(d) for d in labels]
            elif best_key[0] == 'culture':
                labels = data_bin['values']
                labels.sort(key=culture_ordering)
                labels = [str(d) for d in labels]
            else:
                labels = data_bin['values']
            print('%s|- %s [%i]' % (' ' * indent, ', '.join(labels), len(filtered_data)))
            split_data(filtered_data, filter_keys + [best_key[0]], indent + 3)

print('Hierarchy')
split_data(data.data, [], 0)
