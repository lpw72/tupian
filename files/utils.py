import qiniu
from django.conf import settings
from qiniu import Auth, BucketManager

def get_qiniu_auth():
    """获取七牛云认证对象"""
    return Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)

def generate_upload_token(filename, category):
    """生成七牛云上传凭证"""
    q = get_qiniu_auth()
    key = f'{category}/{filename}' if category else filename
    policy = {
        'saveKey': key,
        'deadline': 3600  # 1小时有效期
    }
    token = q.upload_token(settings.QINIU_BUCKET_NAME, key, 3600, policy)
    return token, key

def delete_qiniu_file(key):
    """删除七牛云文件"""
    q = get_qiniu_auth()
    bucket = BucketManager(q)
    ret, info = bucket.delete(settings.QINIU_BUCKET_NAME, key)
    return ret, info

def get_file_url(key):
    """获取文件访问URL"""
    return f'http://{settings.QINIU_DOMAIN}/{key}'