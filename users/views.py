from rest_framework import generics, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializers import UserSerializer, UserProfileSerializer
from .models import UserProfile


class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # 移除认证要求

    def get_queryset(self):
        queryset = User.objects.all()
        # 使用prefetch_related来优化查询性能，避免N+1问题
        return queryset.prefetch_related('userprofile')


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # 移除认证要求


@api_view(['GET', 'PUT'])
@permission_classes([])  # 移除认证要求
def user_profile_detail(request, user_id):
    """
    获取或更新用户简介的API端点
    """
    try:
        user = User.objects.get(id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response({
                'user_id': user.id,
                'username': user.username,
                **serializer.data
            }, status=200)
        
        elif request.method == 'PUT':
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
            
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)