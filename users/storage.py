import boto3
from botocore.client import Config
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class RustFSStorage(S3Boto3Storage):
    """
    自定义存储后端，用于连接RustFS对象存储服务
    """
    def __init__(self):
        # 从环境变量或settings中获取RustFS配置
        self.access_key = getattr(settings, 'RUSTFS_ACCESS_KEY', 'rustfsadmin')
        self.secret_key = getattr(settings, 'RUSTFS_SECRET_KEY', 'rustfsadmin123')
        self.endpoint_url = getattr(settings, 'RUSTFS_ENDPOINT_URL', 'http://rustfs:9000')
        self.bucket_name = getattr(settings, 'RUSTFS_BUCKET_NAME', 'user-avatars')
        self.region_name = getattr(settings, 'RUSTFS_REGION_NAME', 'us-east-1')
        
        # 调用父类构造函数
        super().__init__(
            access_key=self.access_key,
            secret_key=self.secret_key,
            bucket_name=self.bucket_name,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            # 使用路径风格访问，适用于大多数S3兼容存储
            signature_version='s3v4',
            addressing_style='path'
        )

    def url(self, name):
        """
        重写url方法，直接返回预签名URL
        """
        return self.generate_presigned_url(name, expire=3600)

    def generate_presigned_url(self, name, expire=3600):
        """
        生成预签名URL，用于临时访问私有文件
        """
        s3_client = self.connection.meta.client
        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': name},
                ExpiresIn=expire,
                HttpMethod='GET'
            )
            return response
        except Exception as e:
            print(f"生成预签名URL失败: {e}")
            return None