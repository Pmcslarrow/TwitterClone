import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.delete_like import lambda_handler

class TestDeleteLike(unittest.TestCase):

    @patch('lambda_functions.delete_like.boto3')
    @patch('lambda_functions.delete_like.datatier')
    def test_successful_delete(self, mock_datatier, mock_boto3):
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
        mock_datatier.retrieve_all_rows.return_value = [('user1', 20001)]
        mock_datatier.perform_action.return_value = None

        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], "Successfully removed like from the Likes table.")

    @patch('lambda_functions.delete_like.boto3')
    @patch('lambda_functions.delete_like.datatier')
    def test_like_not_found(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls: No existing like is found
        mock_datatier.retrieve_all_rows.return_value = []

        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], "Like not found for given userid and postid.")

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