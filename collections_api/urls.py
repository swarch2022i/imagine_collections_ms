from django.urls import path
from collections_api import views

urlpatterns = [
    path('owner', views.OwnerView.as_view()),
    path('collection', views.CollectionView.as_view()),
    path('image', views.ImageView.as_view()),
]
