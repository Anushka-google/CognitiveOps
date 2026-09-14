import logging
import boto3
from botocore.exceptions import ClientError
import os

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv("AWS_S3_BUCKET_NAME", "cognitiveops-production-data")
        # boto3 automatically picks up AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from env
        self.s3_client = boto3.client('s3')
        
    def upload_dataset(self, file_path: str, object_name: str = None) -> bool:
        """Phase 14.1: Upload ML Datasets or Raw Data to S3"""
        if object_name is None:
            object_name = os.path.basename(file_path)
            
        try:
            logger.info(f"Uploading {file_path} to s3://{self.bucket_name}/{object_name}")
            self.s3_client.upload_file(file_path, self.bucket_name, f"datasets/{object_name}")
            return True
        except ClientError as e:
            logger.error(f"Failed to upload to S3: {e}")
            return False
            
    def download_model_artifact(self, object_name: str, download_path: str) -> bool:
        """Phase 14.1: Download ML Models from S3 for inference"""
        try:
            logger.info(f"Downloading s3://{self.bucket_name}/models/{object_name} to {download_path}")
            self.s3_client.download_file(self.bucket_name, f"models/{object_name}", download_path)
            return True
        except ClientError as e:
            logger.error(f"Failed to download from S3: {e}")
            return False

# Singleton instance
s3_service = S3Service()
