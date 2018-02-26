import click
import json
import requests
import spacy
import transaction

from collections import Counter
from lxml import html
from pyramid.paster import (get_appsettings, setup_logging, )
from pyramid.scripts.common import parse_vars

from ..models.meta import Base
from ..models import (get_engine, get_session_factory, get_tm_session,
                      Group, Item)
from ..ioschema import (ItemSchema, MaterialSchema, DynastySchema, ImageSchema, OwnerSchema, PlaceSchema, PersonSchema)


def echo_line(text, nl=True):
    click.echo('%s%s' % (text, ' ' * (click.get_terminal_size()[0] - len(text))), nl=nl)


@click.command()
@click.argument('config_uri')
@click.argument('source_file', type=click.File('r'))
def load_data(config_uri, source_file):
    """Load the JSON source file into the database."""
    settings = get_appsettings(config_uri)

    click.echo('Loading JSON data\r', nl=False)
    schema = ItemSchema(include_schemas=(MaterialSchema, DynastySchema, ImageSchema, OwnerSchema, PlaceSchema, PersonSchema))
    raw = json.load(source_file)
    data = schema.load(raw, many=True)
    click.echo('Loading JSON data %s' % click.style('✓', fg='green'))

    with transaction.manager:
        dbsession = get_tm_session(get_session_factory(get_engine(settings)), transaction.manager)
        with click.progressbar(data, label='Importing Items', fill_char='=') as data:
            for item_data in data:
                item = Item(attributes=item_data)
                dbsession.add(item)


KEYS = [('maker', None),
        ('materials', 'term'),
        ('category', None),
        ('processed_place_made', None),
        ('processed_culture', None),
        ('made_in', 'name'),
        ('dynasties', 'dynasty')]

def best_effort_bins(values, target_bin_count):
    """Bin values to generate as even a distribution as possible, ignoring the actual values"""
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
    """Order dynasties numerically"""
    if isinstance(value, dict):
        return value['values'][0]
    else:
        return value


def culture_ordering(value):
    """Order cultures by the given ordering"""
    if isinstance(value, dict):
        value = value['values'][0]
    return ['Chalcolithic',
            'Chalcolithic; Late Neolithic',
            'Late Neolithic',
            'Predynastic Period',
            'Predynastic Period; Early Dynastic Period',
            'Early Dynastic Period',
            'Early Dynastic Period; Old Kingdom',
            'Old Kingdom',
            'Old Kingdom; First Intermediate Period',
            'Old Kingdom; Middle Kingdom',
            'First Intermediate Period',
            'First Intermediate Period; Middle Kingdom',
            'Middle Kingdom',
            'Middle Kingdom; New Kingdom',
            'Middle Kingdom; Second Intermediate Period',
            'Hyksos',
            'Nubian',
            'Napatan',
            'Napatan; Meroitic',
            'Meroitic',
            'Hyksos; Second Intermediate Period',
            'Hyksos; New Kingdom',
            'Second Intermediate Period',
            'Second Intermediate Period; New Kingdom',
            'Second Intermediate Period; Hyksos',
            'New Kingdom',
            'New Kingdom; Third Intermediate Period',
            'New Kingdom; Late Period',
            'Late Bronze Age',
            'Third Intermediate Period',
            'Third Intermediate Period; Late Period',
            'Late Period',
            'Late Period; Phoenician',
            'Late Period; Phoenician; Ptolemaic',
            'Late Period; Roman',
            'Late Period; Modern',
            'Late Cypriot I',
            'Late Cypriot I; Late Cypriot II',
            'Late Cypriot II',
            'Late Period; Ptolemaic',
            'Ptolemaic',
            'Ptolemaic; Roman',
            'Roman',
            'Phoenician',
            'Byzantine',
            'Cypriot',
            'Mycenaen',
            'French',
            'Egyptian',
            'Modern',
            'Unknown'].index(value)


def culture_merge(culture1, culture2):
    """Don't merge these cultures with previous cultures."""
    return culture2[-1].split(';')[-1] not in ['Cypriot', 'French', 'Unknown']


def location_ordering(value):
    """Order locations by depth and alphabetically."""
    if isinstance(value, dict):
        value = value['values'][0]
    return [loc.strip() for loc in value.split(':')]


def location_merge(location1, location2):
    """Don't merge locations if they are at different levels or if the parent levels differ."""
    location1 = location1[-1].split(':')
    location2 = location2[0].split(':')
    if len(location1) != len(location2):
        return False
    elif location1[:-1] != location2[:-1]:
        return False
    else:
        return True

def ordered_bins(values, target_size, ordering, allow_merge, single_value=True):
    """Bin the values based on the ordering and merge the bins where merging is allowed."""
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
            if allow_merge(bins[idx]['values'], bins[idx + 1]['values']) and bins[idx]['total'] + bins[idx + 1]['total'] <= target_size:
                for v in bins[idx + 1]['values']:
                    if v not in bins[idx]['values']:
                        bins[idx]['values'].append(v)
                bins[idx]['total'] = bins[idx]['total'] + bins[idx + 1]['total']
                del bins[idx + 1]
                merged = True
                break
        if not merged:
            break
    return bins


def split_data(dbsession, group, filter_keys=None, progress=''):
    """Recursively split the data."""
    if filter_keys is None:
        filter_keys = []
    keys = [k for k in KEYS if k[0] not in filter_keys]
    data = dbsession.query(Item).filter(Item.groups.contains(group))
    if data.count() <= 70 or len(keys) == 0:
        return
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
        if len(ids) / data.count() > best[0] or (len(ids) / data.count() > best[0] and len(counter) < best[1]):
            best = (len(ids) / data.count(), len(counter))
            best_key = (key, access)
            best_values = counter.most_common()
    # Bin the values
    if best_key[0] == 'dynasty':
        bins = ordered_bins(best_values, 70, dynasty_ordering, lambda a, b: True, False)
    elif best_key[0] == 'processed_culture':
        bins = ordered_bins(best_values, 70, culture_ordering, culture_merge)
    elif best_key[0] == 'processed_place_made':
        bins = ordered_bins(best_values, 70, location_ordering, location_merge)
    else:
        bins = best_effort_bins(best_values, min(10, int(data.count() / 20)))
        bins.sort(key=lambda b: ', '.join([str(v) for v in b['values']]))
    bin_length = len([b for b in bins if b['total'] > 0])
    idx = 0
    # If there is only one bin, then ignore this key
    if bin_length == 1:
        split_data(dbsession, group, filter_keys + [best_key[0]], progress)
    else:
        for data_bin in bins:
            if data_bin['total'] > 0:
                # Generate labels
                if best_key[0] == 'dynasty':
                    label = data_bin['values']
                    label.sort(key=dynasty_ordering)
                    if len(label) == 1:
                        label = '%i. Dynasty' % label
                    else:
                        label = '%i.-%i. Dynasties' % (label[0], label[-1])
                elif best_key[0] == 'processed_culture':
                    label = data_bin['values']
                    label = [p.strip() for l in label for p in l.split(';')]
                    label.sort(key=culture_ordering)
                    label = [str(d) for d in label]
                    if len(label) == 1:
                        label = label[0]
                    else:
                        label = '%s - %s' % (label[0], label[-1])
                elif best_key[0] == 'processed_place_made':
                    label = [l.split(':')[-1].strip() for l in data_bin['values']]
                    label.sort(key=location_ordering)
                    parent = [l.strip() for l in data_bin['values'][0].split(':')]
                    if len(parent) > 3:
                        label = '%s (%s)' % (', '.join([str(d) for d in label]), ', '.join(parent[2:][-3:-1]))
                    else:
                        label = ', '.join([str(d) for d in label])
                else:
                    label = ', '.join([str(v) for v in data_bin['values']])
                # Generate the group and assign items to it
                child_group = Group(title=label, parent=group, order=idx)
                dbsession.add(child_group)
                for item in data:
                    matches = False
                    for (key, access), value in [(best_key, v) for v in data_bin['values']]:
                        if isinstance(item[key], list):
                            for x in item[key]:
                                if x:
                                    if access:
                                        if x[access] == value:
                                            matches = True
                                            break
                                    elif x == value:
                                        matches = True
                                        break
                        elif item[key] == value:
                            matches = True
                            break
                    if matches:
                        child_group.items.append(item)
                echo_line('\rGenerating group assignments%s' % click.style('%s %i/%i' % (progress, idx + 1, bin_length), fg='yellow'), nl=False)
                split_data(dbsession, child_group, filter_keys + [best_key[0]], '%s %i/%i' % (progress, idx + 1, bin_length))
                idx = idx + 1


@click.command()
@click.argument('config_uri')
def generate_hierarchy(config_uri):
    """Generate the item hierarchy structure."""
    settings = get_appsettings(config_uri)
    session_factory = get_session_factory(get_engine(settings))
    click.echo('Removing old group assignments', nl=False)
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        for root in dbsession.query(Group).filter(Group.parent_id == None):
            dbsession.delete(root)
    click.echo('\rRemoving old group assignments %s' % click.style('✓', fg='green'))
    with transaction.manager:
        click.echo('Initial group assignment', nl=False)
        dbsession = get_tm_session(session_factory, transaction.manager)
        group = Group(title='Ancient Egypt')
        dbsession.add(group)
        for item in dbsession.query(Item):
            group.items.append(item)
        click.echo('\rInitial group assignment %s' % click.style('✓', fg='green'))
        click.echo('Generating group assignments', nl=False)
        split_data(dbsession, group)
        echo_line('\rGenerating group assignments %s' % click.style('✓', fg='green'))


@click.command()
@click.argument('config_uri')
def link_wikipedia(config_uri):
    """Link groups and items to Wikipedia articles."""
    settings = get_appsettings(config_uri)
    session_factory = get_session_factory(get_engine(settings))
    nlp = spacy.load('en')
    cache = {}
    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)
        query = dbsession.query(Group)
        with click.progressbar(query, length=query.count(), label='Processing Groups', fill_char='=') as result:
            for group in result:
                group['wikipedia'] = []
                for token in nlp(group.title.replace(' - ', ' to ')).noun_chunks:
                    response = requests.post('https://en.wikipedia.org/w/api.php', {'action': 'opensearch', 'format': 'json', 'limit': 30, 'search': str(token)})
                    data = response.json()
                    page_title = None
                    for idx, desc in enumerate(data[2]):
                        if 'Ancient' in desc and 'Egypt' in desc:
                            page_title = data[1][idx]
                    if page_title is None:
                        for idx, desc in enumerate(data[2]):
                            if 'Egypt' in desc:
                                page_title = data[1][idx]
                    if page_title is None and data[1]:
                        page_title = data[1][0]
                    if page_title:
                        if page_title in cache:
                            group['wikipedia'].append(cache[page_title])
                        else:
                            response = requests.post('https://en.wikipedia.org/w/api.php', {'action': 'query', 'format': 'json', 'prop': 'extracts', 'titles': page_title, 'redirects': ''})
                            data = response.json()
                            page = list(data['query']['pages'].values())[0]
                            extract = {'title': page['title'],
                                       'blocks': [html.tostring(elem).decode('utf-8').strip() for elem in html.fragments_fromstring(page['extract']) if elem.text_content() != '']}
                            group['wikipedia'].append(extract)
                            cache[page_title] = extract
