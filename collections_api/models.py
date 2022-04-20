from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipTo, ArrayProperty

# Create your models here.


class Owner(StructuredNode):
    """ Model for the owner of a collection """
    uid = StringProperty(unique_index=True, required=True, max_length=100)
    collection = RelationshipTo('ImageCollection', 'OWNED_BY')

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'uid': self.uid
        }

    def __str__(self):
        return f'uid: {self.uid}'


class ImageCollection(StructuredNode):
    """ Model for a collection of images """
    uid = UniqueIdProperty()
    images_ids = ArrayProperty(base_property=StringProperty(), required=True)
    description = StringProperty(default='Sin Descripción', max_length=250)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'uid': self.uid,
            'images_ids': self.images_ids,
            'description': self.description
        }

    def __str__(self):
        return f'uid: {self.uid} images_ids: {self.images_ids}'
