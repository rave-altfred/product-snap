import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
import uuid
from datetime import timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version='s3v4')
        )
        self.bucket = settings.S3_BUCKET
    
    def upload_file(
        self,
        file: BinaryIO,
        filename: str,
        content_type: str,
        folder: str = "uploads"
    ) -> str:
        """Upload a file to S3 and return the URL."""
        key = f"{folder}/{uuid.uuid4()}/{filename}"
        
        try:
            self.s3_client.upload_fileobj(
                file,
                self.bucket,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'private'
                }
            )
            
            # Return the S3 key (not a public URL since files are private)
            return f"s3://{self.bucket}/{key}"
        except ClientError as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def upload_bytes(
        self,
        data: bytes,
        filename: str,
        content_type: str,
        folder: str = "uploads"
    ) -> str:
        """Upload bytes to S3 and return the URL."""
        key = f"{folder}/{uuid.uuid4()}/{filename}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                ACL='private'
            )
            
            return f"s3://{self.bucket}/{key}"
        except ClientError as e:
            logger.error(f"Failed to upload bytes: {e}")
            raise
    
    def get_signed_url(self, s3_url: str, expiration: int = 3600) -> str:
        """Generate a signed URL for private file access."""
        # Parse s3://bucket/key format
        if not s3_url.startswith("s3://"):
            return s3_url
        
        parts = s3_url.replace("s3://", "").split("/", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid S3 URL: {s3_url}")
        
        bucket, key = parts
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise
    
    def delete_file(self, s3_url: str) -> bool:
        """Delete a file from S3."""
        if not s3_url.startswith("s3://"):
            return False
        
        parts = s3_url.replace("s3://", "").split("/", 1)
        if len(parts) != 2:
            return False
        
        bucket, key = parts
        
        try:
            self.s3_client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def download_file(self, s3_url: str) -> Optional[bytes]:
        """Download a file from S3."""
        if not s3_url.startswith("s3://"):
            return None
        
        parts = s3_url.replace("s3://", "").split("/", 1)
        if len(parts) != 2:
            return None
        
        bucket, key = parts
        
        try:
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Failed to download file: {e}")
            return None


storage_service = StorageService()
