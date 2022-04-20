
from collections_api import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

NO_DATA = {
    'response': {
        'status': '400',
        'error': 'No data provided'
    }
}


class OwnerView(APIView):
    """ A viewset for viewing and editing user instances. """

    def get(self, request, format=None):
        """Handle getting an object by its ID."""
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=NO_DATA)
        if not data.get('uid'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No uid provided'})
        owner = models.Owner.nodes.get_or_none(uid__exact=data.get('uid'))
        if not owner:
            # TODO: Search how to redirect to the url to create a new owner
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Owner not found'})
        nodes = owner.collection.all()
        data = {
            'response': {
                'status': '200',
                'rows': len(nodes),
                'data': [nodes.serialize for nodes in nodes],
            },
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """Handle creating an object."""
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=NO_DATA)
        if not data.get('uid'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'No uid provided'})
        owner = models.Owner.nodes.get_or_none(uid__exact=data.get('uid'))
        if owner:
            return Response(status=status.HTTP_409_CONFLICT, data={'error': 'Owner already exists'})
        owner = models.Owner(uid=data.get('uid'))
        owner.save()
        data = {
            'response': {
                'status': '201',
                'data': owner.serialize,
            },
        }
        return Response(data, status=status.HTTP_201_CREATED)


class CollectionView(APIView):
    """ A viewset for viewing and editing user instances. """

    def get(self, request, format=None):
        """Handle getting an object by its ID."""
        nodes = models.ImageCollection.nodes.all()
        data = {
            'response': {
                'status': '200',
                'rows': len(nodes),
                'data': [nodes.serialize for nodes in nodes],
            },
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        """Handle creating an object."""
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=NO_DATA)
        uid = models.Owner.nodes.get_or_none(
            uid__exact=data.get('uid', None))
        if not uid:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'uid is required'})
        images_ids = data.get('images_ids', None)
        if not images_ids:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'images_ids is required'})
        collection = models.ImageCollection(
            images_ids=images_ids, description=data.get('description', None))
        collection.save()
        uid.collection.connect(collection)
        data = {
            'response': {
                'status': '201',
                'rows': 1,
                'data': [collection.serialize],
            }
        }
        return Response(status=status.HTTP_201_CREATED, data=data)

    def patch(self, request, format=None):
        """Handle updating an object. """
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=NO_DATA)
        if not data.get('uid_owner', None):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'uid of owner is required'})
        owner = models.Owner.nodes.get_or_none(
            uid__exact=data.get('uid_owner', None))
        if not owner:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'owner is not found'})
        if not data.get('uid_collection', None):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'uid of collection is required'})
        collection = owner.collection.search(
            uid__exact=data.get('uid_collection', None))
        if not collection:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'collection is not found'})
        collection = collection.pop()
        if data.get('description', None):
            collection.description = data.get('description')
        if data.get('images_ids', None):
            collection.images_ids = list(
                set(collection.images_ids).symmetric_difference(set(data.get('images_ids'))))
        collection.save()
        data = {
            'response': {
                'status': '200',
                'rows': 1,
                'data': [collection.serialize],
            }
        }
        return Response(status=status.HTTP_200_OK, data=data)

    def delete(self, request, format=None):
        """ Handle deleting an object. """
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=NO_DATA)
        if not data.get('uid_owner', None):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'uid of owner is required'})
        owner = models.Owner.nodes.get_or_none(
            uid__exact=data.get('uid_owner', None))
        if not owner:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'owner not found'})
        if not data.get('uid_collection', None):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'uid of collection is required'})
        i_collection = owner.collection.search(
            uid__exact=data.get('uid_collection', None))
        if not i_collection:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'collection not found'})
        owner.collection.disconnect(i_collection[0])
        i_collection[0].delete()
        data = {
            'response': {
                'status': '200',
                'rows': 1,
                'message': 'collection deleted',
            }
        }
        return Response(status=status.HTTP_200_OK, data=data)
