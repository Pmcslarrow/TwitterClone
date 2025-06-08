import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.get_user import lambda_handler

class TestGetUser(unittest.TestCase):

    @patch('lambda_functions.get_user.boto3')
    @patch('lambda_functions.get_user.datatier')
    def test_get_user_is_following(self, mock_datatier, mock_boto3):
        """Tests getting a user profile that the current user is following."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock the sequence of DB calls
        mock_datatier.retrieve_one_row.side_effect = [
            ('target_id', 'target_bio', 'target_pic.jpg'), # 1. Get profile
            (1,),  # 2. Is following? Yes.
            None   # 3. Is blocked? No.
        ]
        
        event = {"body": json.dumps({"current_userid": "user1", "username": "target_user"})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['bio'], 'target_bio')
        self.assertTrue(body['is_following'])
        self.assertFalse(body['is_blocked'])

    @patch('lambda_functions.get_user.boto3')
    @patch('lambda_functions.get_user.datatier')
    def test_user_not_found(self, mock_datatier, mock_boto3):
        """Tests the case where the requested user profile does not exist."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock the first DB call to return nothing
        mock_datatier.retrieve_one_row.return_value = None

        event = {"body": json.dumps({"current_userid": "user1", "username": "nonexistent_user"})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 404)
        self.assertIn("User not found", json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()