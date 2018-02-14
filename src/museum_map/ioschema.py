"""
##################################################################
:mod:`museum_map.models` - Models used for loading collection data
##################################################################

Items are the main organisational structure, with all other classes
linked from within the individual items.
"""
from marshmallow import post_load, fields
from compound_jsonapi.schema import Schema
from compound_jsonapi.fields import Relationship


class ItemSchema(Schema):
    """Each collection item consists of the following fields:

    * id (string): unique id
    * title (string): title to show to the user
    * accession_no (string): accession number used for cataloguing
    * place_collected (string): description of where the item was collected
    * date_collected (string): date at which the item was collected
    * place_made (string): description of where the item was created
    * date_made (string): date at which the item was made
    * collector (string): description of the item's original collector
    * note (string): cataloguer notes
    * measurements (string): item's size
    * culture (string): which culture the item belongs to
    * description (string): textual description of the item
    * maker (string): description of the entity who made the item
    * category (string): item category

    and the following relationships:

    * materials: materials the item is made of
    * images: images of the item
    * owners: previous owners of the item
    * collected_in: places the item was collected in
    * made_in: places the item was made in
    """
    id = fields.Str()
    title = fields.Str()
    accession_no = fields.Str()
    place_collected = fields.Str()
    date_made = fields.Str()
    collector = fields.Str()
    date_collected = fields.Str()
    note = fields.Str()
    measurements = fields.Str()
    place_made = fields.Str()
    culture = fields.Str()
    processed_culture = fields.Str()
    description = fields.Str()
    maker = fields.Str()
    category = fields.Str()

    materials = Relationship(schema='MaterialSchema',
                             type_='materials',
                             many=True)
    images = Relationship(schema='ImageSchema',
                          type_='images',
                          many=True)
    owners = Relationship(schema='OwnerSchema',
                          type_='owners',
                          many=True)
    collected_in = Relationship(schema='PlaceSchema',
                                type_='places',
                                many=True)
    made_in = Relationship(schema='PlaceSchema',
                           type_='places',
                           many=True)

    class Meta:
        type_ = 'items'


class MaterialSchema(Schema):
    """Materials have the following fields:

    * id (string): unique id
    * term (string): the material's name
    * category (string): the broader category the material belongs to
    """
    id = fields.Str()
    term = fields.Str()
    category = fields.Str()

    class Meta:
        type_ = 'materials'


class ImageSchema(Schema):
    """Images have the following fields:

    * id (string): unique id
    * size (string): one of thumbnail, medium, or large
    * path (string): absolute path to use for image loading
    * width (int): image width in pixels
    * height (int): image height in pixels
    * primary (boolean): whether this image is the item's primary image
    """
    id = fields.Str()
    size = fields.Str()
    path = fields.Str()
    width = fields.Int()
    height = fields.Int()
    primary = fields.Boolean()

    class Meta:
        type_ = 'images'


class PersonSchema(Schema):
    """A person can be both a human or an organisational entity. Each person has
    the following fields:

    * id (string): unique identifier
    * preferred_name (string): the person's preferred name
    * friendly_name (string): a simplified version of the name
    * gender (string): the person's gender
    * deceased (boolean): whether the person is still alive
    * bio (string): a short biography
    * birth_date (string): date of birth if known
    * birth_place (string): location of birth if known
    * death_date (string): date of death if deceased and known
    * death_place (string): location of death if deceased and known
    * cause_of_death (string): cause of death if deceased and known
    * nationality (string): nationality
    * description (string): a longer biography
    """
    id = fields.Str()
    preferred_name = fields.Str()
    friendly_name = fields.Str()
    gender = fields.Str()
    deceased = fields.Boolean()
    bio = fields.Str()
    birth_date = fields.Str()
    birth_place = fields.Str()
    death_date = fields.Str()
    death_place = fields.Str()
    cause_of_death = fields.Str()
    nationality = fields.Str()
    description = fields.Str()

    class Meta:
        type_ = 'people'


class OwnerSchema(Schema):
    """The owner is a previous owner of an item and has the following fields:

    * id (string): unique id
    * how_acquired (string): how the owner aquired the item
    * disposal_method (string): how the owner disposed of the item
    * relationship (string): relationship between the owner and the item
    * begin_date (string): date the owner acquired the item
    * end_date (string): date the owner disposed of the item
    * friendly_name (string): friendly name of the owner

    and relationships:

    * person: The person that holds details of the owner
    """
    id = fields.Str()
    how_acquired = fields.Str()
    disposal_method = fields.Str()
    relationship = fields.Str()
    begin_date = fields.Str()
    end_date = fields.Str()
    name = fields.Str()
    friendly_name = fields.Str()

    person = Relationship(schema='PersonSchema',
                          type_='people')

    class Meta:
        type_ = 'owners'


class PlaceSchema(Schema):
    """Places have the following fields:

    * id (string): unique id
    * name (string): place name
    * start_lat (float): Latitude of the place
    * start_lon (float): Longitude of the place
    * end_lat (float): Unused
    * end_lon (float): Unused
    * collections_lat (float): Same as start_lat
    * collections_lon (float): Same as start_lon

    and relationships:

    * broader: The place that this place belongs to
    """
    id = fields.Str()
    name = fields.Str()
    start_lat = fields.Float(missing=None)
    start_lon = fields.Float(missing=None)
    end_lat = fields.Float(missing=None)
    end_lon = fields.Float(missing=None)
    collections_lat = fields.Float(missing=None)
    collections_lon = fields.Float(missing=None)

    broader = Relationship(schema='PlaceSchema',
                           type_='places',
                           missing=None)

    class Meta:
        type_ = 'places'
