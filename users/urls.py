from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.user_list, name='user-list'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),
    path('users/<int:user_id>/profile/', views.user_profile_detail, name='user-profile-detail'),
]