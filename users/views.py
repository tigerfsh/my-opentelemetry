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
from rest_framework.response import Response
from .models import UserProfile
from .pydantic_schemas import UserSchema, UserCreate, UserUpdate, UserProfileSchema
from pydantic import ValidationError
import json


@api_view(['GET', 'POST'])
@permission_classes([])
def user_list(request):
    """
    获取用户列表或创建新用户
    """
    if request.method == 'GET':
        users = User.objects.prefetch_related('userprofile').all()
        
        # 将Django模型转换为字典，然后验证和序列化
        users_data = []
        for user in users:
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
            # 添加用户资料
            try:
                profile = user.userprofile
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
                user_dict['userprofile'] = profile_dict
            except UserProfile.DoesNotExist:
                pass
            
            try:
                validated_user = UserSchema(**user_dict)
                users_data.append(validated_user.model_dump())
            except ValidationError as e:
                return JsonResponse({'error': f'数据验证失败: {str(e)}'}, status=400)
        
        return JsonResponse(users_data, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_data = UserCreate(**data)
            
            # 检查用户名是否已存在
            if User.objects.filter(username=user_data.username).exists():
                return JsonResponse({'error': '用户名已存在'}, status=400)
            
            # 检查邮箱是否已存在
            if user_data.email and User.objects.filter(email=user_data.email).exists():
                return JsonResponse({'error': '邮箱已被使用'}, status=400)
                
            # 创建用户
            user = User.objects.create_user(
                username=user_data.username,
                email=user_data.email,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                password=user_data.password
            )
            
            # 为新用户创建资料
            UserProfile.objects.get_or_create(user=user)
            
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
            
            try:
                validated_user = UserSchema(**user_dict)
                return JsonResponse(validated_user.model_dump(), status=201)
            except ValidationError as e:
                return JsonResponse({'error': f'数据验证失败: {str(e)}'}, status=400)
                
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append(f"{error['loc'][0]}: {error['msg']}")
            return JsonResponse({'error': errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'创建用户失败: {str(e)}'}, status=500)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([])
def user_detail(request, pk):
    """
    获取、更新或删除特定用户
    """
    try:
        user = User.objects.prefetch_related('userprofile').get(pk=pk)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)

    if request.method == 'GET':
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
        
        try:
            profile = user.userprofile
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
            user_dict['userprofile'] = profile_dict
        except UserProfile.DoesNotExist:
            pass
        
        try:
            validated_user = UserSchema(**user_dict)
            return JsonResponse(validated_user.model_dump())
        except ValidationError as e:
            return JsonResponse({'error': f'数据验证失败: {str(e)}'}, status=400)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            user_update_data = UserUpdate(**data)
            
            # 更新用户字段
            if user_update_data.username is not None:
                # 检查新用户名是否与其他用户冲突
                existing_user = User.objects.filter(username=user_update_data.username).exclude(pk=user.pk)
                if existing_user.exists():
                    return JsonResponse({'error': '用户名已存在'}, status=400)
                user.username = user_update_data.username
            
            if user_update_data.email is not None:
                # 检查新邮箱是否与其他用户冲突
                existing_user = User.objects.filter(email=user_update_data.email).exclude(pk=user.pk)
                if existing_user.exists():
                    return JsonResponse({'error': '邮箱已被使用'}, status=400)
                user.email = user_update_data.email
            
            if user_update_data.first_name is not None:
                user.first_name = user_update_data.first_name
            
            if user_update_data.last_name is not None:
                user.last_name = user_update_data.last_name
            
            if user_update_data.password is not None and user_update_data.password != '':
                user.set_password(user_update_data.password)
            
            user.save()
            
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
            
            try:
                profile = user.userprofile
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
                user_dict['userprofile'] = profile_dict
            except UserProfile.DoesNotExist:
                pass
            
            validated_user = UserSchema(**user_dict)
            return JsonResponse(validated_user.model_dump())
            
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append(f"{error['loc'][0]}: {error['msg']}")
            return JsonResponse({'error': errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': '无效的JSON数据'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'更新用户失败: {str(e)}'}, status=500)

    elif request.method == 'DELETE':
        try:
            user.delete()
            return JsonResponse({'message': '用户删除成功'}, status=204)
        except Exception as e:
            return JsonResponse({'error': f'删除用户失败: {str(e)}'}, status=500)


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
            
            try:
                validated_profile = UserProfileSchema(**profile_dict)
                response_data = {
                    'user_id': user.id,
                    'username': user.username,
                    **validated_profile.model_dump()
                }
                return Response(response_data, status=200)
            except ValidationError as e:
                return Response({'error': f'数据验证失败: {str(e)}'}, status=400)
        
        elif request.method == 'PUT':
            # 对于文件上传，需要使用request.FILES而不是request.data
            profile_dict = {}
            for field in ['bio', 'phone_number', 'location', 'birth_date']:
                if field in request.data:
                    profile_dict[field] = request.data[field]
            
            # 处理文件上传
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            
            for attr, value in profile_dict.items():
                setattr(profile, attr, value)
            
            try:
                profile.save()
                validated_profile = UserProfileSchema.from_orm(profile)
                return Response(validated_profile.model_dump(), status=200)
            except ValidationError as e:
                errors = {}
                for error in e.errors():
                    field = error['loc'][0]
                    msg = error['msg']
                    errors[field] = msg
                return Response(errors, status=400)
            except Exception as e:
                return Response({'error': str(e)}, status=400)
            
    except User.DoesNotExist:
        return Response({'error': '用户不存在'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)