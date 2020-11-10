import click
import json
import os
import requests

from collections import Counter
from itertools import chain
from inflection import singularize, titleize


IGNORE = ['empty categories with no backlinks', 'with']
NO_INFLECTION = ["women's clothes", "men's clothes"]
MANUAL_INFLECTION = {
    "women's": 'Women',
    "men's": 'Men',
}
CACHE = {}
HIERARCHY_MAPPINGS = {}


def dbpedia_concept_expand_one_level(concept):
    identifier = concept.lower()
    identifier = concept[0].upper() + concept[1:]
    identifier = f'Category:{identifier.replace(" ", "_")}'
    result = []
    if identifier in CACHE:
        data = CACHE[identifier]
    else:
        url = f'https://dbpedia.demo.openlinksw.com/data/{identifier}.json'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            CACHE[identifier] = data
        else:
            data = {}
    if f'http://dbpedia.demo.openlinksw.com/resource/{identifier}' in data:
        fields = data[f'http://dbpedia.demo.openlinksw.com/resource/{identifier}']
        if 'http://www.w3.org/2004/02/skos/core#broader' in fields:
            for value in fields['http://www.w3.org/2004/02/skos/core#broader']:
                value = value['value'][53:].replace('_', ' ')
                if value.lower() not in IGNORE:
                    if concept not in HIERARCHY_MAPPINGS:
                        HIERARCHY_MAPPINGS[concept] = [value]
                    elif value not in HIERARCHY_MAPPINGS[concept]:
                        HIERARCHY_MAPPINGS[concept].append(value)
                    result.append(value)
    else:
        pass
    return result


def expand_concept(concept):
    if concept.strip() == '':
        return []
    result = []
    if ' ' in concept:
        if ' for ' in concept:
            if ' for a ' in concept:
                idx = concept.find(' for a ')
                result.extend(expand_concept(concept[0:idx].strip()))
                result.extend(expand_concept(concept[idx + 7:].strip()))
            else:
                pass
        elif '(' in concept:
            idx1 = concept.find('(')
            idx2 = concept.find(')', idx1)
            result.extend(expand_concept(concept[0:idx1].strip()))
            result.extend(expand_concept(concept[idx1 + 1:idx2].strip()))
            result.extend(expand_concept(concept[idx2 + 1:].strip()))
        elif '&' in concept:
            for part in concept.split('&'):
                result.extend(expand_concept(part.strip()))
        elif ' and ' in concept:
            idx = concept.find(' and ')
            result.extend(expand_concept(concept[0:idx].strip()))
            result.extend(expand_concept(concept[idx + 5:].strip()))
        else:
            for part in concept.split(' '):
                result.extend(expand_concept(part.strip()))
    else:
        if concept.lower() not in IGNORE:
            if concept.lower() in NO_INFLECTION:
                concept = titleize(concept)
            elif concept.lower() in MANUAL_INFLECTION:
                concept = MANUAL_INFLECTION[concept.lower()]
            else:
                concept = titleize(singularize(concept))
            result.append(concept)
            result.extend(dbpedia_concept_expand_one_level(concept))
    return result


def print_tree(categories, category, indent=''):
    print(f'{indent}{category["label"]}')
    #print(category)
    children = [categories[c] for c in category['children']]
    children.sort(key=lambda c: c['label'].split())
    for child in children:
        print_tree(categories, child, indent=f'{indent}  ')


def break_cycles(categories, category, visited=None):
    #if visited:
    #    print(len(visited))
    #print(visited)
    for c in list(category['children']):
        if visited is None:
            break_cycles(categories, categories[c], visited=[category['label']])
        elif c not in visited:
            break_cycles(categories, categories[c], visited=visited + [category['label']])
        else:
            categories[c]['parents'].remove(category['label'])
            category['children'].remove(c)


def assign_item(categories, category, item_id):
    categories[category]['items'].add(item_id)
    for parent in categories[category]['parents']:
        assign_item(categories, parent, item_id)


@click.command()
@click.argument('source')
@click.pass_context
def load(ctx):
    global CACHE
    if os.path.exists('cache.json'):
        with open('cache.json') as in_f:
            CACHE = json.load(in_f)
    new_objects = []
    categories = {}
    for basepath, _, filenames in os.walk('../va-downloader/data-transformed'):
        for filename in filenames:
            if filename.endswith('.json'):
                with open(os.path.join(basepath, filename)) as in_f:
                    data = json.load(in_f)
                new_objects.append(data)
                concepts.extend(data['object'])
                #concepts = set([])
                #for concept in data['object']:
                #    concepts.add(concept.lower())
                #for concept in concepts:
                #    if concept not in categories:
                #        categories[concept] = {
                #            'label': concept,
                #            'parents': None,
                #            'children': [],
                #            'height': 0,
                #            'items': set(),
                #        }
    '''old_len = 0
    new_len = len(categories)
    while old_len != new_len:
        #print(f'{old_len} -> {new_len}')
        old_len = new_len
        for category in list(categories.values()):
            if category['parents'] is None:
                category['parents'] = []
                if category['height'] >= 6:
                    continue
                #if not dbpedia_concept_expand_one_level(category['label']):
                #    print(category['label'])
                for new_concept in dbpedia_concept_expand_one_level(category['label']):
                    new_concept = new_concept.lower()
                    if ' by ' in new_concept:
                        continue
                    if ' in ' in new_concept:
                        continue
                    #print(f'{category["label"]} -> {new_concept}')
                    if new_concept in categories:
                        if category['label'] not in categories[new_concept]['children']:
                            categories[new_concept]['children'].append(category['label'])
                    else:
                        categories[new_concept] = {
                            'label': new_concept,
                            'parents': None,
                            'children': [category['label']],
                            'height': category['height'] + 1,
                            'items': set(),
                        }
                    if new_concept not in category['parents']:
                        category['parents'].append(new_concept)
        new_len = len(categories)
    with open('cache.json', 'w') as out_f:
        json.dump(CACHE, out_f)
    #print('-------------')
    for category in categories.values():
        if not category['parents']:
            break_cycles(categories, category)
    #print('-------------')
    for obj in new_objects:
        for label in obj['object']:
            assign_item(categories, label.lower(), obj['id'])
    tmp = list(categories.values())
    tmp.sort(key=lambda c: len(c['items']), reverse=True)
    for category in tmp:
        if not category['parents']:
            print(f'{len(category["items"])}: {category["label"]}')
        #    print_tree(categories, category)
    '''
