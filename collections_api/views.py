from http.client import OK, CREATED, NOT_FOUND, BAD_REQUEST, NO_CONTENT, CONFLICT

from collections_api import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

COLLECTION_UTRL = '/api/collection'
IMAGE_URL = '/api/image'
OWNER_URL = '/api/owner'
OWNER_NOT_FOUND = 'Owner not found'

MISSING_DATA = {
    'status': BAD_REQUEST,
    'error': 'Missing data',
    'message': 'The request is missing required data.'
}

NOT_FOUND_ERR = {
    'status': NOT_FOUND,
    'error': 'Resource not found',
    'message': '',
}

ALREADY_EXISTS = {
    'status': CONFLICT,
    'error': 'Already exists',
}


class ImageView(APIView):
    """ View for the image model """

    def delete(self, request):
        """ Delete an image """
        data = request.data
        if 'uuid' not in data.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST, content_type='application/json', data=MISSING_DATA)
        image = models.Image.nodes.get_or_none(uuid__exact=data.get('uuid'))
        if not image:
            NOT_FOUND_ERR['message'] = f'Image with uuid {data.get("uuid")} not found'
            return Response(status=status.HTTP_404_NOT_FOUND, content_type='application/json', data=NOT_FOUND_ERR)
        image.delete()
        data = {'status': NO_CONTENT, 'message': 'Image deleted'}
        return Response(data, status=status.HTTP_204_NO_CONTENT, content_type='application/json')


class OwnerView(APIView):
    """ A viewset for viewing and editing user instances. """

    def get(self, request):
        """Handle getting an object by its ID."""
        data = request.query_params
        if not data.get('uuid'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        owner = models.Owner.nodes.get_or_none(uuid__exact=data.get('uuid'))
        if not owner:
            NOT_FOUND_ERR['message'] = OWNER_NOT_FOUND
            NOT_FOUND_ERR['redirect'] = f'{request.get_host()}{OWNER_URL}'
            return Response(status=status.HTTP_404_NOT_FOUND, data=NOT_FOUND_ERR)

        nodes = owner.collection.all()
        data = {
            'status': OK,
            'rows': len(nodes),
            'data': [nodes.owner_serialize for nodes in nodes],
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """Handle creating an object."""
        data = request.data
        if not data.get('uuid'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        owner = models.Owner.nodes.get_or_none(uuid__exact=data.get('uuid'))
        if owner:
            return Response(status=status.HTTP_409_CONFLICT, data=ALREADY_EXISTS)

        owner = models.Owner(uuid=data.get('uuid'))
        owner.save()
        data = {
            'status': CREATED,
        }
        return Response(data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        """Handle deleting an object."""
        data = request.query_params
        if not data.get('uuid'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        owner = models.Owner.nodes.get_or_none(uuid__exact=data.get('uuid'))
        if not owner:
            NOT_FOUND_ERR['message'] = OWNER_NOT_FOUND
            NOT_FOUND_ERR['redirect'] = f'{request.get_host()}{OWNER_URL}'
            return Response(status=status.HTTP_404_NOT_FOUND, data=NOT_FOUND_ERR)
        owner.delete()
        data = {
            'status': NO_CONTENT,
        }
        return Response(data, status=status.HTTP_204_NO_CONTENT)


class CollectionView(APIView):
    """ A viewset for viewing and editing user instances. """

    def get(self, request):
        """Handle getting an object by its ID."""
        uuid = request.query_params.get('uuid', None)
        if not uuid:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        data = {
            'status': OK,
            'collection': models.ImageCollection.nodes.get_or_none(uuid__exact=uuid).serialize,
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """Handle creating an object."""
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        uuid = models.Owner.nodes.get_or_none(
            uuid__exact=data.get('uuid', None))
        if not uuid:
            NOT_FOUND_ERR['message'] = OWNER_NOT_FOUND
            NOT_FOUND_ERR['redirect'] = f'{request.get_host()}{OWNER_URL}'
            return Response(status=status.HTTP_404_NOT_FOUND, data=NOT_FOUND_ERR)

        images_ids = data.get('images_ids', None)
        if not images_ids:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        collection = models.ImageCollection(
            description=data.get('description', None))
        collection.save()
        collection.connect(images_ids, uuid)
        data = {
            'status': CREATED,
            'message': 'Collection created',
            'uuid': repr(collection),
        }
        return Response(status=status.HTTP_201_CREATED, data=data)

    def patch(self, request, format=None):
        """Handle updating an object. """
        key = 'uuidCollection'
        data = request.data
        if key not in data.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        collection = models.ImageCollection.nodes.first_or_none(
            uuid__exact=data.get(key))
        if not collection:
            NOT_FOUND_ERR['message'] = 'Collection not found'
            return Response(status=status.HTTP_404_NOT_FOUND, data=NOT_FOUND_ERR)

        collection.update(images_ids=data.get('images_ids', None),
                          description=data.get('description', None))
        collection.save()
        data = {
            'status': OK,
            'collection': collection.serialize,
        }
        return Response(status=status.HTTP_200_OK, data=data)

    def delete(self, request, format=None):
        """ Handle deleting an object. """
        key = 'uuidCollection'
        data = request.data
        if key not in data.keys():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=MISSING_DATA)

        collection = models.ImageCollection.nodes.first_or_none(
            uuid__exact=data.get(key))
        if not collection:
            NOT_FOUND_ERR['message'] = 'Collection not found'
            return Response(status=status.HTTP_404_NOT_FOUND, data=NOT_FOUND_ERR)
        collection.delete()
        data = {
            'status': NO_CONTENT,
            'message': 'collection deleted',
        }
        return Response(status=status.HTTP_204_NO_CONTENT, data=data)
