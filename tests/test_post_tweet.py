import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.post_tweet import lambda_handler

class TestPostTweet(unittest.TestCase):

    @patch('lambda_functions.post_tweet.boto3')
    @patch('lambda_functions.post_tweet.datatier')
    def test_successful_tweet_posting(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock the database action
        mock_datatier.perform_action.return_value = None

        # Create a valid event
        event = {
            "body": json.dumps({
                "userid": "123",
                "textcontent": "This is a valid tweet."
            })
        }
        
        response = lambda_handler(event, None)
        
        # Assert the response is successful
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(json.loads(response["body"])["message"], "Post posted successfully.")
        
        # Verify the database action was called correctly
        mock_datatier.perform_action.assert_called_once_with(
            mock_conn,
            "\n                INSERT INTO PostInfo (userid, dateposted, textcontent, image_file_key, reply_to_postid)\n                VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s);\n            ",
            ['123', 'This is a valid tweet.', None, None]
        )

    @patch('lambda_functions.post_tweet.boto3')
    @patch('lambda_functions.post_tweet.datatier')
    def test_successful_tweet_with_image(self, mock_datatier, mock_boto3):
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        mock_datatier.perform_action.return_value = None

        # Create event with an image key
        event = {
            "body": json.dumps({
                "userid": "123",
                "textcontent": "This is a valid tweet with an image.",
                "image_file_key": "uploads/123/image1.jpg"
            })
        }
        
        response = lambda_handler(event, None)
        
        # Assert success
        self.assertEqual(response["statusCode"], 200)
        
        # Verify the image key was passed to the database action
        mock_datatier.perform_action.assert_called_once_with(
            mock_conn,
            "\n                INSERT INTO PostInfo (userid, dateposted, textcontent, image_file_key, reply_to_postid)\n                VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s);\n            ",
            ['123', 'This is a valid tweet with an image.', 'uploads/123/image1.jpg', None]
        )

    def test_tweet_exceeding_character_limit(self):
        # This test doesn't need mocks as it fails validation first
        event = {
            "body": json.dumps({
                "userid": "123",
                "textcontent": "A" * 501  # 501 characters
            })
        }
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(json.loads(response["body"])["message"], "Text content exceeds 500 characters.")

    def test_missing_parameters(self):
        # Test missing userid
        event_no_userid = {"body": json.dumps({"textcontent": "This tweet has no userid."})}
        response_no_userid = lambda_handler(event_no_userid, None)
        self.assertEqual(response_no_userid["statusCode"], 400)
        self.assertEqual(json.loads(response_no_userid["body"])["message"], "userid missing.")
        
        # Test missing textcontent
        event_no_text = {"body": json.dumps({"userid": "123"})}
        response_no_text = lambda_handler(event_no_text, None)
        self.assertEqual(response_no_text["statusCode"], 400)
        self.assertEqual(json.loads(response_no_text["body"])["message"], "textcontent missing.")

if __name__ == '__main__':
    unittest.main()