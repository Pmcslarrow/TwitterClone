import boto3


CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

import uuid
import os
import json
from configparser import ConfigParser


def lambda_handler(event, context):
    """
    Generate Presigned URL
    ----------------------
    The client should use this URL to get a presigned 
    URL for uploading an image to S3. It also gives a file key 
    which can be used to reference the location of the image in S3,
    kept inside the database. 
    
    Input example:
        event = {
            "headers": CORS_HEADERS,
                                "body": json.dumps({
                "userid": "12345",
                "postid": "67890",
                "fileType": "image/png"
            })
        }

    Output example:
        {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json" },
            "headers": CORS_HEADERS,
                                "body": json.dumps({
                "uploadUrl": "<presigned_url>",
                "fileKey": "<file_key>"
            })
        }
    """
    try:
        s3 = boto3.client('s3')
        body = json.loads(event['body'])
        user_id = body['userid']
        post_id = body['postid']
        file_type = body.get('fileType', 'image/png')

        file_extension = "png"  
        file_key = f"uploads/{user_id}/{post_id}/{uuid.uuid4()}.{file_extension}"

        BUCKET = 'twitter-clone-uploads'

        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET,
                'Key': file_key,
                'ContentType': file_type
            },
            ExpiresIn=300  # 5 minutes
        )

        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json" },
            "headers": CORS_HEADERS,
                                "body": json.dumps({
                "uploadUrl": presigned_url,
                "fileKey": file_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 400,
                        "headers": CORS_HEADERS,
                                "body": json.dumps({ "error": str(e) })
        }
