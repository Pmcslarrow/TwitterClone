import pytest
from unittest.mock import patch, MagicMock
import json
from lambda_functions.generate_presigned_url import lambda_handler

@patch('boto3.client')
def test_generate_presigned_url_success(mock_boto_client):
    # Mock S3 client and presigned URL
    mock_s3 = MagicMock()
    mock_boto_client.return_value = mock_s3
    mock_s3.generate_presigned_url.return_value = "https://mock-s3-url.com"

    # Mock event
    event = {
        "body": json.dumps({
            "userid": "12345",
            "postid": "67890",
            "fileType": "image/png"
        })
    }

    # Call the lambda_handler
    response = lambda_handler(event, None)

    # Assertions
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert "uploadUrl" in body
    assert "fileKey" in body
    assert body["uploadUrl"] == "https://mock-s3-url.com"
    assert body["fileKey"].startswith("uploads/12345/67890/")

@patch('boto3.client')
def test_generate_presigned_url_missing_userid(mock_boto_client):
    # Mock event with missing userid
    event = {
        "body": json.dumps({
            "postid": "67890",
            "fileType": "image/png"
        })
    }

    # Call the lambda_handler
    response = lambda_handler(event, None)

    # Assertions
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert "error" in body