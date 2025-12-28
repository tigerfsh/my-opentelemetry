import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '确保RustFS上的avatars bucket存在'

    def handle(self, *args, **options):
        # 从settings获取RustFS配置
        access_key = getattr(settings, 'RUSTFS_ACCESS_KEY', 'rustfsadmin')
        secret_key = getattr(settings, 'RUSTFS_SECRET_KEY', 'rustfsadmin123')
        endpoint_url = getattr(settings, 'RUSTFS_ENDPOINT_URL', 'http://rustfs:9000')
        bucket_name = getattr(settings, 'RUSTFS_BUCKET_NAME', 'user-avatars')
        region_name = getattr(settings, 'RUSTFS_REGION_NAME', 'us-east-1')

        # 创建S3客户端
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region_name
        )

        # 尝试创建bucket（如果不存在）
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            self.stdout.write(
                self.style.SUCCESS(f'Bucket {bucket_name} 已存在')
            )
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                # Bucket不存在，创建它
                try:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': region_name}
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'成功创建bucket {bucket_name}')
                    )
                except ClientError as create_error:
                    self.stdout.write(
                        self.style.ERROR(f'创建bucket失败: {create_error}')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(f'检查bucket时出错: {e}')
                )