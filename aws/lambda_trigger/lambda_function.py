import json
import urllib.request
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Phase 14.3: Event-Driven AWS Lambda
    Triggered automatically by AWS S3 when a new dataset is uploaded.
    """
    logger.info("Lambda triggered by S3 Event")
    
    # Extract S3 bucket and file name from the event
    try:
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        logger.info(f"New dataset detected: s3://{bucket_name}/{object_key}")
        
        # Trigger the CognitiveOps Backend Retraining API
        # In production, this would be the EC2 public IP or Load Balancer URL
        backend_url = os.environ.get("COGNITIVEOPS_BACKEND_URL", "http://localhost:8000")
        retrain_endpoint = f"{backend_url}/api/v1/mlops/trigger-retraining"
        
        logger.info(f"Triggering Retraining API at {retrain_endpoint}...")
        
        payload = json.dumps({
            "dataset_uri": f"s3://{bucket_name}/{object_key}",
            "source": "aws_lambda_s3_trigger"
        }).encode('utf-8')
        
        req = urllib.request.Request(
            retrain_endpoint, 
            data=payload, 
            headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {os.environ.get("API_SECRET")}'}
        )
        
        with urllib.request.urlopen(req) as response:
            res_body = response.read()
            logger.info(f"Backend Response: {res_body}")
            
        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully triggered retraining for {object_key}')
        }
        
    except Exception as e:
        logger.error(f"Error processing S3 event: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Error triggering CognitiveOps pipeline')
        }
