from django.core.management.base import BaseCommand
from django.conf import settings
from qiniu import Auth, BucketManager
from files.models import File
from users.models import CustomUser
from categories.models import Category

class Command(BaseCommand):
    help = 'Sync files from Qiniu to database'

    def handle(self, *args, **options):
        # 获取管理员用户
        admin_user = CustomUser.objects.filter(username='admin').first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('Admin user not found'))
            return

        # 获取七牛云文件列表
        q = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        bucket = BucketManager(q)
        bucket_name = settings.QINIU_BUCKET_NAME

        # 列出所有文件
        prefix = None
        marker = None
        limit = 1000
        delimiter = None

        while True:
            ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
            if ret.get('items'):
                for item in ret['items']:
                    key = item['key']
                    # 解析类别和描述
                    parts = key.split('/')
                    if len(parts) >= 2:
                        category_name, description = parts[0], parts[1]
                    else:
                        category_name, description = '其他', key

                    # 获取或创建类别
                    category, _ = Category.objects.get_or_create(name=category_name)

                    # 检查文件是否已存在
                    file_url = f'http://{settings.QINIU_DOMAIN}/{key}'
                    if not File.objects.filter(url=file_url).exists():
                        File.objects.create(
                            user=admin_user,
                            description=description,
                            category=category,
                            url=file_url
                        )
                        self.stdout.write(self.style.SUCCESS(f'Created file: {description}'))

            if eof:
                break
            marker = ret.get('marker')

        self.stdout.write(self.style.SUCCESS('File sync completed'))