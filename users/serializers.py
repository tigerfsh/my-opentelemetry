from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    # 自定义日期字段格式
    birth_date = serializers.DateField(format='%Y-%m-%d', input_formats=['%Y-%m-%d', 'iso-8601'], required=False, allow_null=True)
    
    def to_internal_value(self, data):
        # 处理空字符串的日期字段，将其转换为None
        if 'birth_date' in data and (data['birth_date'] == '' or data['birth_date'] is None):
            data = data.copy()  # 避免修改原始数据
            data['birth_date'] = None
        return super().to_internal_value(data)
    
    class Meta:
        model = UserProfile
        fields = ('id', 'bio', 'phone_number', 'location', 'birth_date', 'avatar', 'thumbnail')
        read_only_fields = ('thumbnail',)  # thumbnail should be read-only


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer(read_only=True)

    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password', 'date_joined', 'is_staff', 'userprofile')

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        
        # 确保用户简介存在
        UserProfile.objects.get_or_create(user=user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if password:
            instance.set_password(password)
            instance.save()
            
        return instance
