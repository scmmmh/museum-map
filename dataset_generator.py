import json

from csv import DictReader

from museum_map.models import ItemSchema

BASEPATH = '/home/mhall/Documents/Data/NML_Egypt'

# Load the materials
materials = {}
with open('%s/Materials.csv' % BASEPATH) as in_f:
    reader = DictReader(in_f)
    for line in reader:
        materials[line['Id']] = {'id': line['Id'],
                                 'category': line['MaterialDescriptor'],
                                 'term': line['Term']}

# Load the people
people = {}
with open('%s/People.csv' % BASEPATH) as in_f:
    reader = DictReader(in_f)
    for line in reader:
        people[line['LinkId']] = {'id': line['LinkId'],
                                  'preferred_name': line['PreferredName'],
                                  'friendly_name': line['FriendlyName'],
                                  'gender': line['Gender'],
                                  'deceased': line['Deceased'] == '1',
                                  'bio': line['BriefBio'],
                                  'birth_date': line['BirthDate'],
                                  'birth_place': line['BirthPlace'],
                                  'death_date': line['DeathDate'],
                                  'death_place': line['DeathPlace'],
                                  'cause_of_death': line['CauseOfDeath'],
                                  'nationality': line['Nationality'],
                                  'description': line['Description']}

# Load the owners
owners = {}
with open('%s/ItemsOwners.csv' % BASEPATH) as in_f:
    reader = DictReader(in_f)
    for line in reader:
        owners[line['AuthLinkKey']] = {'id': line['AuthLinkKey'],
                                       'how_acquired': line['HowAcquired'],
                                       'disposal_method': line['DisposalMethod'],
                                       'relationship': line['Relationship'],
                                       'begin_date': line['BeginDate'],
                                       'end_date': line['EndDate'],
                                       'name': line['Name'],
                                       'friendly_name': line['FriendlyName'],
                                       'person': people[line['LinkId']]}

# Load the images
images = {}
with open('%s/CollectionImages.csv' % BASEPATH) as in_f:
    reader = DictReader(in_f)
    for line in reader:
        images[line['ImageId']] = {'id': line['ImageId'],
                                   'size': 'large' if line['ImageType'] == '3' else 'medium' if line['ImageType'] == '2' else 'thumbnail',
                                   'path': line['ImagePath'],
                                   'width': int(line['Width']),
                                   'height': int(line['Height']),
                                   'primary': line['IsPrimaryImage'] == '1'}

# Load the places
next_place_id = 0
places = {}
with open('%s/Places.csv' % BASEPATH) as in_f:
    reader = DictReader(in_f)
    for line in reader:
        next_place_id = max(next_place_id, int(line['PlaceKey']))
        places[line['PlaceKey']] = {'id': line['PlaceKey'],
                                    'name': line['Place1'],
                                    'start_lat': float(line['StartLatitude']) if line['StartLatitude'] else None,
                                    'start_lon': float(line['StartLongitude']) if line['StartLongitude'] else None,
                                    'end_lat': float(line['EndLatitude']) if line['EndLatitude'] else None,
                                    'end_lon': float(line['EndLongitude']) if line['EndLongitude'] else None,
                                    'collections_lat': float(line['CollectionsLatitude']) if line['CollectionsLatitude'] else None,
                                    'collections_lon': float(line['CollectionsLongitude']) if line['CollectionsLongitude'] else None,
                                    'broader': line['BroaderKey'],
                                    'broader-text': line['BroaderText']}
next_place_id = next_place_id + 1
# Link the broader elements and missing broader places
for key, value in list(places.items()):
    if value['broader'] not in places:
        broader_places = [s.strip() for s in value['broader-text'].split(';')]
        last_id = None
        while len(broader_places) > 1:
            found = False
            for value2 in places.values():
                if value2['name'] == broader_places[0]:
                    last_id = value2['id']
                    found = True
                    break
            if not found:
                places[str(next_place_id)] = {'id': str(next_place_id),
                                              'name': broader_places[0],
                                              'broader': places[last_id] if last_id else None}
                last_id = str(next_place_id)
                next_place_id = next_place_id + 1
            broader_places = broader_places[1:]
        places[value['broader']] = {'id': value['broader'],
                                    'name': broader_places[0],
                                    'broader': places[last_id] if last_id else None}
    value['broader'] = places[value['broader']]
# Create the place specialisations
place_mappings = {}
for filename in ['ItemsPlacesCollected.csv', 'ItemsPlacesMade.csv']:
    with open('%s/%s' % (BASEPATH, filename)) as in_f:
        reader = DictReader(in_f)
        for line in reader:
            if line['Locale']:
                localeId = '%s::%s' % (line['PlaceKey'], line['Locale'])
                if localeId not in place_mappings:
                    place_mappings[localeId] = str(next_place_id)
                    places[str(next_place_id)] = {'id': str(next_place_id),
                                                  'name': line['Locale'],
                                                  'broader': places[line['PlaceKey']]}
                    next_place_id = next_place_id + 1

# Load the collection items
def load_relationship(filename, item_id, collection, related_key):
    related = []
    with open('%s/%s' % (BASEPATH, filename)) as in_f:
        reader = DictReader(in_f)
        for line in reader:
            if line['MimsyKey'] == item_id:
                if 'Locale' in line and line['Locale']:
                    related.append(collection[place_mappings['%s::%s' % (line[related_key], line['Locale'])]])
                else:
                    related.append(collection[line[related_key]])
    return related

items = []
with open('%s/CollectionItems.csv' % BASEPATH) as in_f:
    reader = DictReader(in_f)
    for line in reader:
        item = {'id': line['MimsyKey'],
                'accession_no': line['AccessionNo'],
                'place_collected': line['PlaceCollected'],
                'date_made': line['DateMade'],
                'collector': line['Collector'],
                'date_collected': line['DateCollected'],
                'note': line['Note'],
                'title': line['Title'],
                'measurements': line['Measurements'],
                'place_made': line['PlaceMade'],
                'culture': line['Culture'],
                'description': line['Description'],
                'maker': line['Maker'],
                'category': line['ItemName'],
                'materials': load_relationship('ItemsMaterials.csv',
                                               line['MimsyKey'],
                                               materials,
                                               'MaterialId'),
                'images': load_relationship('CollectionItemImages.csv',
                                            line['MimsyKey'],
                                            images,
                                            'ImageId'),
                'owners': load_relationship('ItemsOwners.csv',
                                            line['MimsyKey'],
                                            owners,
                                            'AuthLinkKey'),
                'collected_in': load_relationship('ItemsPlacesCollected.csv',
                                                  line['MimsyKey'],
                                                  places,
                                                  'PlaceKey'),
                'made_in': load_relationship('ItemsPlacesMade.csv',
                                             line['MimsyKey'],
                                             places,
                                             'PlaceKey')}
        items.append(item)


# Serialise result
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
with open('%s/dataset.json' % BASEPATH, 'w') as out_f:
    print(json.dumps(schema.dump(items, many=True).data), file=out_f)
