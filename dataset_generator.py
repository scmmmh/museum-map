import json
import sys

from csv import DictReader

from museum_map.ioschema import (ItemSchema, MaterialSchema, ImageSchema, OwnerSchema, PlaceSchema, PersonSchema)

BASEPATH = sys.argv[1]

# Load the materials
print('Loading materials')
materials = {}
with open('%s/Materials.csv' % BASEPATH) as in_f:
    reader = DictReader(in_f)
    for line in reader:
        materials[line['Id']] = {'id': line['Id'],
                                 'category': line['MaterialDescriptor'],
                                 'term': line['Term']}

# Load the people
print('Loading people')
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
print('Loading owners')
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
print('Loading images')
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
print('Loading places')
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


unknown = set()
def process_culture(culture):
    if culture == '':
        return 'Unknown'
    elif culture == 'Predyndastic Period (Naqada II) or Early Dynastic Period':
        return 'Predynastic Period; Early Dynastic Period'
    elif culture == 'Late Period or Modern':
        return 'Later Period; Modern'
    elif culture == 'Ptolemaic Period':
        return 'Ptolemaic'
    elif culture == 'Old Kingdom':
        return 'Old Kingdom'
    elif culture == 'Cypriot':
        return 'Cypriot'
    elif culture == 'Third Intermediate Period; Late Period':
        return 'Third Intermediate Period; Late Period'
    elif culture == 'Ptolemaic':
        return 'Ptolemaic'
    elif culture == 'Late Period - Ptolemaic':
        return 'Late Period; Ptolemaic'
    elif culture == 'New Kingdom or Third Intermediate Period':
        return 'New Kingdom; Third Intermediate Period'
    elif culture == 'New Kingdom (Ramesside Period); Third Intermediate Period':
        return 'New Kingdom; Third Intermediate Period'
    elif culture == 'Late Old Kingdom - First Intermediate Period':
        return 'Old Kingdom; First Intermediate Period'
    elif culture == 'Nubian (A Group)':
        return 'Nubian'
    elif culture == 'Second Intermediate Period; New Kingdom':
        return 'Second Intermediate Period; New Kingdom'
    elif culture == 'Probably New Kingdom or later':
        return 'New Kingdom'
    elif culture == 'Hyksos; Second Intermediate Period':
        return 'Hyksos; Second Intermediate Period'
    elif culture == 'Mycenaean':
        return 'Mycenaen'
    elif culture == 'Chalcolithic; Late Neolithic':
        return 'Chalcolithic; Late Neolithic'
    elif culture == 'New Kingdom or later':
        return 'New Kingdom'
    elif culture == 'First Intermediate Period - Middle Kingdom':
        return 'First Intermediate Period; Middle Kingdom'
    elif culture == 'First Intermediate Period':
        return 'First Intermediate Period'
    elif culture == 'Middle Kingdom':
        return 'Middle Kingdom'
    elif culture == 'Late Period or later':
        return 'Late Period'
    elif culture == 'Early Dynastic Period':
        return 'Early Dynastic Period'
    elif culture == 'Egyptian/Phoenician':
        return 'Phoenician'
    elif culture == 'Romano-Egyptian':
        return 'Roman'
    elif culture == 'Late Period/Phoenician':
        return 'Late Period; Phoenician'
    elif culture == 'Second Intermediate Period':
        return 'Second Intermediate Period'
    elif culture == 'Late Period or after':
        return 'Late Period'
    elif culture == 'Hyksos or New Kingdom':
        return 'Hyksos; New Kingdom'
    elif culture == 'Unknown':
        return 'Unknown'
    elif culture == 'Late Period: Saite':
        return 'Late Period'
    elif culture == 'Ptolemaic or Romano-Egyptian':
        return 'Ptolemaic; Roman'
    elif culture == 'Third Intermeidate Period':
        return 'Third Intermediate Period'
    elif culture == 'Early Dynastic':
        return 'Early Dynastic Period'
    elif culture == 'Romano-Egyptian or earlier':
        return 'Roman'
    elif culture == 'French':
        return 'French'
    elif culture == 'New Kingdom':
        return 'New Kingdom'
    elif culture == 'Middle Kingdom to New Kingdom':
        return 'Middle Kingdom; New Kingdom'
    elif culture == 'Early New Kingdom':
        return 'New Kingdom'
    elif culture == 'Predynastic Period (Naqada I)':
        return 'Predynastic Period'
    elif culture == 'Predynastic Period (Naqada II)':
        return 'Predynastic Period'
    elif culture == 'Modern':
        return 'Modern'
    elif culture == 'Predynastic Period (Naqada I - II)':
        return 'Predynastic Period'
    elif culture == "Predynastic Period (Naqada III/'Dynasty 0')":
        return 'Predynastic Period; Early Dynastic Period'
    elif culture == 'New Kingdom: Ramesside or later':
        return 'New Kingdom'
    elif culture == 'Second Intermediate Period: Hyksos':
        return 'Second Intermediate Period; Hyksos'
    elif culture == 'Old Kingdom or later':
        return 'Old Kingdom'
    elif culture == 'Late Period':
        return 'Late Period'
    elif culture == 'New Kingdom (Ramesside Period)':
        return 'New Kingdom'
    elif culture == 'Meroitic Period':
        return 'Meroitic'
    elif culture == 'Early Dynastic - early Old Kingdom':
        return 'Early Dynastic Period; Old Kingdom'
    elif culture == 'Third Intermediate Period or alter':
        return 'Third Intermediate Period'
    elif culture == 'Hyksos; New Kingdom':
        return 'Hyksos; New Kingdom'
    elif culture == 'Byzantine':
        return 'Byzantine'
    elif culture == 'Probably Romano-Egyptian':
        return 'Roman'
    elif culture == 'Third Intermediate Period or Late Period':
        return 'Third Intermediate Period; Late Period'
    elif culture == 'Late Bronze Age':
        return 'Late Bronze Age'
    elif culture == 'Middle Kingdom or New Kingdom':
        return 'Middle Kingdom; New Kingdom'
    elif culture == 'Naqada III  – early Dynasty 1':
        return 'Predynastic Period; Early Dynastic Period'
    elif culture == 'Old Kingom or Middle Kingdom':
        return 'Old Kingdom; Middle Kingdom'
    elif culture == 'Third Intermediate Period':
        return 'Third Intermediate Period'
    elif culture == 'New  Kingdom':
        return 'New Kingdom'
    elif culture == 'Third Intermediate Period - Late Period':
        return 'Third Intermediate Period; Late Period'
    elif culture == 'Roman Imperial':
        return 'Roman'
    elif culture == 'Hyksos':
        return 'Hyksos'
    elif culture == 'New Kingdom or Late Period':
        return 'New Kingdom; Late Period'
    elif culture == 'Middle Kingdom; Second Intermediate Period':
        return 'Middle Kingdom; Second Intermediate Period'
    elif culture == 'Third Intermediate Period -  Late Period':
        return 'Third Intermediate Period; Late Period'
    elif culture == 'Middle Kingom':
        return 'Middle Kingdom'
    elif culture == 'Early Dynastic or Old Kingdom':
        return 'Early Dynastic Period; Old Kingdom'
    elif culture == 'Late Period (?)':
        return 'Late Period'
    elif culture == 'Meroitic':
        return 'Meroitic'
    elif culture == 'New Kingdom: Ramesside':
        return 'New Kingdom'
    elif culture == 'Ptolemaic-Romano Egyptian':
        return 'Ptolemaic'
    elif culture == 'Egyptian':
        return 'Egyptian'
    elif culture == 'Old Kingdom - Middle Kingdom':
        return 'Old Kingdom; Middle Kingdom'
    elif culture == 'Late Period - Romano-Egyptian':
        return 'Late Period; Roman'
    elif culture == 'Roman Period':
        return 'Roman'
    elif culture == 'Predynastic':
        return 'Predynastic Period'
    elif culture == 'Early Dynastic Period - Old Kingdom':
        return 'Early Dynastic Period; Old Kingdom'
    elif culture == 'Predynastic Period (Naqada iI)':
        return 'Predynastic Period'
    elif culture == 'Phoenician':
        return 'Phoenician'
    elif culture == 'Byzantine (Coptic)':
        return 'Byzantine'
    elif culture == 'Second Intermediate Period - New Kingdom':
        return 'Second Intermediate Period; New Kingdom'
    elif culture == 'Predynastic Period (Naqada I); Predynastic Period (Naqada II)':
        return 'Predynastic Period'
    elif culture == 'Ptolemaic or later':
        return 'Ptolemaic'
    elif culture == 'Late Period/Phoenician or Ptolemaic':
        return 'Late Period; Phoenician; Ptolemaic'
    elif culture == 'Third Intermediate Period  - Late Period':
        return 'Third Intermediate Period; Late Period'
    elif culture == 'Middle Kingdom or later':
        return 'Middle Kingdom'
    elif culture == 'Roman':
        return 'Roman'
    elif culture == 'Second Intermediate Period – Early New Kingdom':
        return 'Second Intermediate Period; New Kingdom'
    elif culture == 'Predynastic ?':
        return 'Predynastic Period'
    elif culture == 'Late Period or Ptolemaic':
        return 'Late Period; Ptolemaic'
    elif culture == 'Napatan or Meroitic':
        return 'Napatan; Meroitic'
    elif culture == 'Ptolemaic - Romano-Egyptian':
        return 'Ptolemaic; Roman'
    elif culture == 'Late Period - Ptolemaic Period':
        return 'Late Period; Ptolemaic'
    elif culture == 'Middle Kingdom or earlier':
        return 'Middle Kingdom'
    elif culture == 'New Kingdom - Late Period':
        return 'New Kingdom; Late Period'
    elif culture == 'Late Period (Saite)':
        return 'Late Period'
    elif culture == 'Nubian (Pan-Grave)':
        return 'Nubian'
    elif culture == 'Middle Kingdom - Second Intermediate Period':
        return 'Middle Kingdom; Second Intermediate Period'
    elif culture == 'Late Period; Romano-Egyptian':
        return 'Late Period; Roman'
    elif culture == 'Middle Kingdom - New Kingdom':
        return 'Middle Kingdom; New Kingdom'
    elif culture == 'Late Cypriot I; Late Cypriot II':
        return 'Late Cypriot I; Late Cypriot II'
    else:
        unknown.add(culture)
    return culture

# Load the actual items
print('Loading items')
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
                'processed_culture': process_culture(line['Culture']),
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
schema = ItemSchema(include_schemas=(MaterialSchema, ImageSchema, OwnerSchema, PlaceSchema, PersonSchema))
with open('%s/dataset.json' % BASEPATH, 'w') as out_f:
    print(json.dumps(schema.dump(items, many=True)), file=out_f)
