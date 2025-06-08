import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.like_post import lambda_handler

class TestLikePost(unittest.TestCase):

    @patch('lambda_functions.like_post.boto3')
    @patch('lambda_functions.like_post.datatier')
    def test_successful_like(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls: No existing like found
        mock_datatier.retrieve_one_row.return_value = None
        mock_datatier.perform_action.return_value = None

        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], "Successfully added like to the Likes table.")

    @patch('lambda_functions.like_post.boto3')
    @patch('lambda_functions.like_post.datatier')
    def test_already_liked(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls: An existing like is found
        mock_datatier.retrieve_one_row.return_value = ('user1', 20001)

        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 409)
        self.assertEqual(json.loads(response['body'])['message'], "User has already liked this post.")

    def test_missing_userid(self):
        event = {'body': json.dumps({'postid': 20001})}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "userid missing.")

    def test_missing_postid(self):
        event = {'body': json.dumps({'userid': 'user1'})}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], "postid missing.")

if __name__ == '__main__':
    unittest.main()