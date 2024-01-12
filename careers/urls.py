from django.urls import path
from .views import *

urlpatterns = [
    path('', PostViewSet.as_view({'get': 'get', 'post': 'post'}), name='post-list'),
    path('<int:pk>/', PostViewSet.as_view({'get': 'retrieve', 'patch': 'patch', 'delete': 'delete'}), name='post-detail'),
]