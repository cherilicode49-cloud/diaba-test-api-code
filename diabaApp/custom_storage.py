from storages.backends.s3boto3 import S3Boto3Storage


class CustomS3Boto3Storage(S3Boto3Storage):
    """
    Custom S3 storage backend that checks if the file name/path is an external
    direct URL (e.g. from Yiwugo: https://img.yiwugo.com/..., http://..., https://...).
    
    - If it is an external URL, returns the raw URL directly without prefixing S3 bucket domain.
    - If it is a normal uploaded file (e.g. image/product/image/...), delegates to standard S3Boto3Storage.url().
    """

    def url(self, name, parameters=None, expire=None, http_method=None):
        if not name:
            return ""
        name_str = str(name).strip()
        if (
            name_str.startswith("http://")
            or name_str.startswith("https://")
            or "img.yiwugo.com" in name_str
            or "yfimg.yiwugo.com" in name_str
        ):
            return name_str
        return super().url(name, parameters=parameters, expire=expire, http_method=http_method)

