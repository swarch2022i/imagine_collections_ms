from neomodel import StructuredNode, StringProperty, UniqueIdProperty, RelationshipTo, RelationshipFrom, cardinality

# Create your models here.


class Image(StructuredNode):
    """ Model for an image """
    uuid = UniqueIdProperty()
    collectionsIn = RelationshipFrom(
        'ImageCollection', 'HAS_IMAGE', cardinality=cardinality.OneOrMore)

    @property
    def serialize(self):
        """Return a serializable version of the node."""
        return self.uuid

    def __str__(self):
        return f'uid: {self.uuid}'


class ImageCollection(StructuredNode):
    """ Model for a collection of images """
    uuid = UniqueIdProperty()
    images = RelationshipTo('Image', 'HAS_IMAGE',
                            cardinality=cardinality.OneOrMore)
    description = StringProperty(default='Sin Descripción', max_length=250)
    owner = RelationshipFrom('Owner', 'OWN',
                             cardinality=cardinality.OneOrMore)

    def update(self, description=None, images_ids=None):
        """ Update the collection """
        if description:
            self.description = description
        if images_ids:
            nodes = Image.get_or_create(*images_ids)
            for node in nodes:
                if self.images.is_connected(node):
                    self.images.disconnect(node)
                    if len(node.collectionsIn.match().all(lazy=True)) == 0:
                        node.delete()
                else:
                    self.images.connect(node)
        self.save()

    def delete(self):
        """ Delete the collection and all the images in it """
        for image in self.images:
            if len(image.collectionsIn.match().all(lazy=True)) == 1:
                image.delete()
        return super().delete()

    def __repr__(self):
        return self.uuid

    def connect(self, images_ids, uuid):
        """ Connect the collection to the images and to the owner """
        self.owner.connect(uuid)
        for image_id in images_ids:
            image = Image.nodes.get_or_none(uuid__exact=image_id)
            if image:
                self.images.connect(image)
            else:
                image = Image(uuid=image_id)
                image.save()
                self.images.connect(image)

    @property
    def owner_serialize(self):
        """Return a serializable version of the node."""
        return {
            'uid': self.uuid,
            'images_ids': [image.serialize for image in self.images.all()[:5]],
            'description': self.description,
        }

    @ property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'images_ids': [image.serialize for image in self.images.all()],
            'description': self.description
        }

    def __str__(self):
        return f'uid: {self.uuid}'


class Owner(StructuredNode):
    """ Model for the owner of a collection """
    uuid = StringProperty(unique_index=True, required=True, max_length=100)
    collection = RelationshipTo(
        'ImageCollection', 'OWN')

    def delete(self):
        """Delete the owner and all the collections owned by the owner"""
        for collection in self.collection.all():
            self.collection.disconnect(collection)
            collection.delete()
        return super().delete()

    @ property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'uid': self.uuid
        }

    def __str__(self):
        return f'uid: {self.uuid}'
