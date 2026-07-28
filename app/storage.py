

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
