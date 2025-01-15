import boto3
import os
from dotenv import load_dotenv
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_anthropic_connection():
    load_dotenv()
    
    # Get AWS credentials from environment
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.getenv('AWS_SESSION_TOKEN')
    aws_region = os.getenv('AWS_REGION')
    
    logger.info("Initializing AWS session")
    logger.debug(f"Using region: {aws_region}")
    
    # Create AWS session
    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_session_token=aws_session_token,
        region_name=aws_region
    )
    
    # Create Bedrock client
    bedrock = session.client(
        service_name='bedrock-runtime',
        region_name=aws_region
    )
    
    try:
        logger.info("Attempting to send message to Claude via AWS Bedrock")
        
        prompt = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello!"
                }
            ]
        }
        
        logger.debug("Sending request to Bedrock")
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps(prompt)
        )
        
        response_body = json.loads(response['body'].read())
        logger.info("Message sent successfully")
        logger.debug(f"Full response: {json.dumps(response_body, indent=2)}")
        
        print("Connection successful!")
        print("Response:", response_body['content'][0]['text'])
        return True
        
    except Exception as e:
        logger.error(f"Connection error occurred: {str(e)}", exc_info=True)
        if hasattr(e, 'response'):
            logger.error(f"Response details: {e.response}")
        print("Connection error:", str(e))
        return False

if __name__ == "__main__":
    test_anthropic_connection()
