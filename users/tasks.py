from celery import shared_task
from django.contrib.auth.models import User
from .models import UserProfile
from PIL import Image
import os
from django.conf import settings


@shared_task
def generate_avatar_thumbnail(user_id):
    """
    生成用户头像缩略图的异步任务
    """
    try:
        user_profile = UserProfile.objects.get(user_id=user_id)
        
        if not user_profile.avatar:
            print(f"用户 {user_id} 没有上传头像")
            return False
            
        # 打开原始头像图像
        avatar_path = user_profile.avatar.path
        
        # 生成缩略图
        image = Image.open(avatar_path)
        image.thumbnail((150, 150))  # 创建150x150像素的缩略图
        
        # 准备缩略图路径
        avatar_dir, avatar_filename = os.path.split(avatar_path)
        name, ext = os.path.splitext(avatar_filename)
        thumbnail_filename = f"{name}_thumbnail{ext}"
        thumbnail_path = os.path.join(avatar_dir, "thumbnails", thumbnail_filename)
        
        # 确保缩略图目录存在
        thumbnail_dir = os.path.dirname(thumbnail_path)
        os.makedirs(thumbnail_dir, exist_ok=True)
        
        # 保存缩略图
        image.save(thumbnail_path)
        
        # 更新用户简介中的缩略图字段
        user_profile.thumbnail.name = os.path.join('avatars/thumbnails', thumbnail_filename)
        user_profile.save()
        
        print(f"成功为用户 {user_id} 生成头像缩略图")
        return True
        
    except UserProfile.DoesNotExist:
        print(f"用户简介 {user_id} 不存在")
        return False
    except Exception as e:
        print(f"生成头像缩略图时出错: {str(e)}")
        return False