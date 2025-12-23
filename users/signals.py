from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from .tasks import generate_avatar_thumbnail


@receiver(post_save, sender=UserProfile)
def trigger_avatar_thumbnail_generation(sender, instance, created, **kwargs):
    """
    当用户简介保存且头像更新时，触发头像缩略图生成任务
    """
    # 只在更新现有用户简介且上传了新头像时触发任务
    if not created and instance.avatar and hasattr(instance, '_avatar_changed') and instance._avatar_changed:
        # 调用异步任务生成缩略图
        generate_avatar_thumbnail.delay(instance.user_id)


# 为了检测头像是否更改，我们需要覆盖UserProfile的save方法
from django.db import models
from PIL import Image
import os


# 保存原始的save方法
original_save = UserProfile.save


def new_save(self, *args, **kwargs):
    # 检查头像是否已更改
    if self.pk:  # 如果是更新现有对象
        old_instance = UserProfile.objects.get(pk=self.pk)
        self._avatar_changed = (old_instance.avatar != self.avatar)
    else:  # 如果是新创建的对象
        self._avatar_changed = bool(self.avatar)
    
    # 调用原始的save方法
    result = original_save(self, *args, **kwargs)
    
    # 如果上传了新头像，触发缩略图生成任务
    if hasattr(self, '_avatar_changed') and self._avatar_changed and self.avatar:
        generate_avatar_thumbnail.delay(self.user_id)
    
    return result


# 将新的save方法赋给UserProfile
UserProfile.save = new_save