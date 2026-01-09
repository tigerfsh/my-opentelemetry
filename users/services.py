from django.contrib.auth.models import User
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from .models import UserProfile
from typing import Optional, Dict, Any
from .exceptions import (
    UserNotFoundException, UsernameExistsException, EmailExistsException,
    InvalidUserDataException, ProfileNotFoundException, InvalidProfileDataException
)


def get_all_users_with_profiles():
    """
    获取所有用户及其资料
    """
    users = User.objects.prefetch_related('userprofile').all()
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
        
        users_data.append(user_dict)
    
    return users_data


def create_user(username: str, email: Optional[str], first_name: Optional[str], 
                last_name: Optional[str], password: str):
    """
    创建新用户及对应的用户资料
    """
    with transaction.atomic():
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            raise UsernameExistsException(f"用户名 '{username}' 已存在")
        
        # 检查邮箱是否已存在
        if email and User.objects.filter(email=email).exists():
            raise EmailExistsException(f"邮箱 '{email}' 已被使用")
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        
        # 为新用户创建资料
        UserProfile.objects.get_or_create(user=user)
        
        return user


def get_user_with_profile(user_id: int):
    """
    根据ID获取特定用户及其资料
    """
    try:
        user = User.objects.prefetch_related('userprofile').get(pk=user_id)
    except User.DoesNotExist:
        raise UserNotFoundException(f"用户ID {user_id} 不存在")
    
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
    
    return user_dict


def update_user(user_id: int, username: Optional[str] = None, email: Optional[str] = None, 
                first_name: Optional[str] = None, last_name: Optional[str] = None, 
                password: Optional[str] = None):
    """
    更新用户信息
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise UserNotFoundException(f"用户ID {user_id} 不存在")
    
    # 检查用户名是否与其他用户冲突
    if username is not None:
        existing_user = User.objects.filter(username=username).exclude(pk=user.pk)
        if existing_user.exists():
            raise UsernameExistsException(f"用户名 '{username}' 已存在")
        user.username = username
    
    # 检查邮箱是否与其他用户冲突
    if email is not None:
        existing_user = User.objects.filter(email=email).exclude(pk=user.pk)
        if existing_user.exists():
            raise EmailExistsException(f"邮箱 '{email}' 已被使用")
        user.email = email
    
    if first_name is not None:
        user.first_name = first_name
    
    if last_name is not None:
        user.last_name = last_name
    
    if password is not None and password != '':
        user.set_password(password)
    
    user.save()
    return user


def delete_user(user_id: int):
    """
    删除用户
    """
    try:
        user = User.objects.get(pk=user_id)
        user.delete()
        return True
    except User.DoesNotExist:
        raise UserNotFoundException(f"用户ID {user_id} 不存在")
    except Exception as e:
        raise InvalidUserDataException(f"删除用户失败: {str(e)}")


def get_or_create_user_profile(user_id: int):
    """
    获取或创建用户资料
    """
    try:
        user = User.objects.get(id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=user)
        return user, profile, created
    except User.DoesNotExist:
        raise UserNotFoundException(f"用户ID {user_id} 不存在")


def update_user_profile(user_id: int, profile_data: Dict[str, Any], files=None):
    """
    更新用户资料
    """
    try:
        user = User.objects.get(id=user_id)
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # 更新普通字段
        for field in ['bio', 'phone_number', 'location', 'birth_date']:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        
        # 处理文件上传
        if files and 'avatar' in files:
            profile.avatar = files['avatar']
        
        profile.save()
        return profile
    except User.DoesNotExist:
        raise UserNotFoundException(f"用户ID {user_id} 不存在")
    except Exception as e:
        raise InvalidProfileDataException(f"更新用户资料失败: {str(e)}")