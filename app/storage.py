import boto3
from app.config import Config
from botocore.exceptions import ClientError


class StorageClient:

    def __init__(self, s3_client, bucket: str, presigned_url_ttl_seconds: int):
        self.s3_client = s3_client 
        self.bucket = bucket
        self.presigned_url_ttl_seconds = presigned_url_ttl_seconds

    def upload(self, key: str, data: bytes, content_type: str) -> None:
        self.s3_client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def delete(self, key: str) -> None:
        self.s3_client.delete_object(Bucket=self.bucket, Key=key)

    def generate_presigned_url(self, key: str) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=self.presigned_url_ttl_seconds
        )

    def download(self, key: str) -> bytes:
        response = self.s3_client.get_object(
            Bucket=self.bucket,
            Key=key
        )
        return response["Body"].read()


def build_s3_client(settings: Config):
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key.get_secret_value(),
        region_name=settings.s3_region,
    )


def get_storage_client(settings: Config) -> StorageClient:
    return StorageClient(
        build_s3_client(settings),
        settings.s3_bucket,
        settings.presigned_url_ttl_seconds,
    )


def ensure_bucket(s3_client, bucket: str) -> None:
    try:
        s3_client.head_bucket(Bucket=bucket)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket)
