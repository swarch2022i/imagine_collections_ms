from django.urls import path, include

from rest_framework.routers import DefaultRouter
from collections_api import views

# router = DefaultRouter()
# router.register('owner', views.OwnerVieSet, basename='owner')

urlpatterns = [
    path('user', views.OwnerView.as_view()),
    path('collection', views.CollectionView.as_view()),
]
