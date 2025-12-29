from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .storage import RustFSStorage


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    avatar = models.ImageField(storage=RustFSStorage(), upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    thumbnail = models.ImageField(storage=RustFSStorage(), upload_to='avatars/thumbnails/', blank=True, null=True, verbose_name='头像缩略图')
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='个人简介')
    location = models.CharField(max_length=30, blank=True, null=True, verbose_name='位置')
    birth_date = models.DateField(null=True, blank=True, verbose_name='生日')

    class Meta:
        verbose_name = '用户简介'
        verbose_name_plural = '用户简介'

    def __str__(self):
        return f'{self.user.username}的简介'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    当创建新用户时，自动创建用户简介
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    当用户信息保存时，同时保存用户简介
    """
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # 如果用户简介不存在，则创建一个
        UserProfile.objects.create(user=instance)