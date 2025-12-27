from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from .serializers import UserSerializer


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # 移除认证要求


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # 移除认证要求