from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime
from typing import Optional

class UserProfileSchema(BaseModel):
    id: Optional[int] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None
    location: Optional[str] = None
    birth_date: Optional[datetime] = None
    avatar: Optional[str] = None
    thumbnail: Optional[str] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=150)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str = Field(..., min_length=1)

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None

class UserSchema(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_joined: datetime
    is_staff: bool
    userprofile: Optional[UserProfileSchema] = None

    class Config:
        from_attributes = True


from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .pydantic_schemas import UserSchema, UserCreate, UserUpdate, UserProfileSchema
from . import services
from pydantic import ValidationError
import json


class UserListView(APIView):
    """
    获取用户列表或创建新用户
    """
    permission_classes = []

    def get(self, request):
        users_data = services.get_all_users_with_profiles()
        
        # 使用Pydantic验证数据
        validated_users = []
        for user_dict in users_data:
            validated_user = UserSchema(**user_dict)
            validated_users.append(validated_user.model_dump())
        
        return JsonResponse(validated_users, safe=False)
    
    def post(self, request):
        data = json.loads(request.body)
        user_data = UserCreate(**data)
        
        # 调用服务层创建用户
        user = services.create_user(
            username=user_data.username,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            password=user_data.password
        )
        
        # 准备响应数据
        user_dict = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined,
            'is_staff': user.is_staff,
            'userprofile': None
        }
        
        validated_user = UserSchema(**user_dict)
        return JsonResponse(validated_user.model_dump(), status=201)


class UserDetailView(APIView):
    """
    获取、更新或删除特定用户
    """
    permission_classes = []

    def get(self, request, pk):
        user_data = services.get_user_with_profile(user_id=pk)
        validated_user = UserSchema(**user_data)
        return JsonResponse(validated_user.model_dump())

    def put(self, request, pk):
        data = json.loads(request.body)
        user_update_data = UserUpdate(**data)
        
        # 调用服务层更新用户
        user = services.update_user(
            user_id=pk,
            username=user_update_data.username,
            email=user_update_data.email,
            first_name=user_update_data.first_name,
            last_name=user_update_data.last_name,
            password=user_update_data.password
        )
        
        # 获取更新后的用户数据
        user_data = services.get_user_with_profile(user_id=pk)
        
        validated_user = UserSchema(**user_data)
        return JsonResponse(validated_user.model_dump())
            
    def delete(self, request, pk):
        success = services.delete_user(user_id=pk)
        if success:
            return JsonResponse({'message': '用户删除成功'}, status=204)
        else:
            return JsonResponse({'error': '删除用户失败'}, status=500)


class UserProfileView(APIView):
    """
    获取或更新用户简介的API端点
    """
    permission_classes = []  # 移除认证要求

    def get(self, request, user_id):
        user, profile, created = services.get_or_create_user_profile(user_id=user_id)
        
        profile_dict = {
            'id': profile.id,
            'bio': profile.bio,
            'phone_number': profile.phone_number,
            'location': profile.location,
            'birth_date': profile.birth_date,
            'avatar': profile.avatar.url if profile.avatar else None,
            'thumbnail': profile.thumbnail.url if profile.thumbnail else None,
            'user_id': profile.user_id
        }
        
        validated_profile = UserProfileSchema(**profile_dict)
        response_data = {
            'user_id': user.id,
            'username': user.username,
            **validated_profile.model_dump()
        }
        return Response(response_data, status=status.HTTP_200_OK)
    
    def put(self, request, user_id):
        # 准备资料数据
        profile_data = {}
        for field in ['bio', 'phone_number', 'location', 'birth_date']:
            if field in request.data:
                profile_data[field] = request.data[field]
        
        # 调用服务层更新用户资料
        profile = services.update_user_profile(
            user_id=user_id,
            profile_data=profile_data,
            files=request.FILES if hasattr(request, 'FILES') and request.FILES else None
        )
        
        validated_profile = UserProfileSchema.from_orm(profile)
        return Response(validated_profile.model_dump(), status=status.HTTP_200_OK)