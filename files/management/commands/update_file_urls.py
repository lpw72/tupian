from django.core.management.base import BaseCommand
from django.conf import settings
from files.models import File
from urllib.parse import urlparse

class Command(BaseCommand):
    help = 'Update file URLs to use new Qiniu domain'

    def handle(self, *args, **options):
        new_domain = settings.QINIU_DOMAIN
        files = File.objects.all()
        count = 0

        for file in files:
            if file.url:
                parsed_url = urlparse(file.url)
                # 替换URL中的域名部分
                new_url = parsed_url._replace(netloc=new_domain).geturl()
                if new_url != file.url:
                    file.url = new_url
                    file.save()
                    count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} file URLs'))