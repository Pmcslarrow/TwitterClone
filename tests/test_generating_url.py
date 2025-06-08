import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.generate_presigned_url import lambda_handler

class TestGeneratePresignedUrl(unittest.TestCase):

    @patch('lambda_functions.generate_presigned_url.uuid.uuid4', return_value='mock-uuid')
    @patch('lambda_functions.generate_presigned_url.boto3')
    def test_generate_presigned_url_success(self, mock_boto3, mock_uuid):
        """Tests the successful generation of a presigned URL."""
        # Mock the S3 client and its method
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.generate_presigned_url.return_value = "https://mock-s3-url.com"

        # Prepare the test event
        event = {
            "body": json.dumps({
                "userid": "user123",
                "postid": "post456",
                "fileType": "image/jpeg"
            })
        }

        # Call the lambda handler
        response = lambda_handler(event, None)

        # Assert the response
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['uploadUrl'], "https://mock-s3-url.com")
        self.assertEqual(body['fileKey'], "uploads/user123/post456/mock-uuid.png")

        # Assert that the S3 client was called with the correct parameters
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'put_object',
            Params={
                'Bucket': 'twitter-clone-uploads',
                'Key': "uploads/user123/post456/mock-uuid.png",
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=300
        )

    def test_missing_required_parameters(self):
        """Tests for missing 'userid' and 'postid' in the event body."""
        # Test case for missing userid
        event_no_userid = {
            "body": json.dumps({
                "postid": "post456",
                "fileType": "image/png"
            })
        }
        response_no_userid = lambda_handler(event_no_userid, None)
        self.assertEqual(response_no_userid['statusCode'], 400)
        body_no_userid = json.loads(response_no_userid['body'])
        self.assertIn("'userid'", body_no_userid['error'])

        # Test case for missing postid
        event_no_postid = {
            "body": json.dumps({
                "userid": "user123",
                "fileType": "image/png"
            })
        }
        response_no_postid = lambda_handler(event_no_postid, None)
        self.assertEqual(response_no_postid['statusCode'], 400)
        body_no_postid = json.loads(response_no_postid['body'])
        self.assertIn("'postid'", body_no_postid['error'])

    @patch('lambda_functions.generate_presigned_url.uuid.uuid4', return_value='mock-uuid')
    @patch('lambda_functions.generate_presigned_url.boto3')
    def test_default_file_type(self, mock_boto3, mock_uuid):
        """Tests that 'image/png' is used as the default ContentType."""
        # Mock the S3 client
        mock_s3_client = MagicMock()
        mock_boto3.client.return_value = mock_s3_client
        mock_s3_client.generate_presigned_url.return_value = "https://mock-s3-url.com"

        # Event without a fileType specified
        event = {
            "body": json.dumps({
                "userid": "user123",
                "postid": "post456"
            })
        }
        
        lambda_handler(event, None)

        # Assert that the S3 client was called with the default ContentType
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'put_object',
            Params={
                'Bucket': 'twitter-clone-uploads',
                'Key': "uploads/user123/post456/mock-uuid.png",
                'ContentType': 'image/png' # Default value
            },
            ExpiresIn=300
        )

if __name__ == '__main__':
    unittest.main()