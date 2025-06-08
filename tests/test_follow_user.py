import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.follow_user import lambda_handler

class TestFollowUser(unittest.TestCase):

    @patch('lambda_functions.follow_user.boto3')
    @patch('lambda_functions.follow_user.datatier')
    def test_follow_user_success(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({
                'host': 'test_host',
                'port': 3306,
                'username': 'test_user',
                'password': 'test_password'
            })
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls
        mock_datatier.retrieve_all_rows.side_effect = [
            [('follower_id',)],  # Follower exists
            [('followee_id',)],  # Followee exists
            [],                  # Not already following
            []                   # Not blocked
        ]
        mock_datatier.perform_action.return_value = None

        event = {
            'body': json.dumps({
                'follower': 'follower_id',
                'followee_username': 'followee_username'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Successfully followed user.')

    @patch('lambda_functions.follow_user.boto3')
    @patch('lambda_functions.follow_user.datatier')
    def test_already_following(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({
                'host': 'test_host',
                'port': 3306,
                'username': 'test_user',
                'password': 'test_password'
            })
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls
        mock_datatier.retrieve_all_rows.side_effect = [
            [('follower_id',)],  # Follower exists
            [('followee_id',)],  # Followee exists
            [('follower_id', 'followee_id')]  # Already following
        ]

        event = {
            'body': json.dumps({
                'follower': 'follower_id',
                'followee_username': 'followee_username'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'User is already following this account.')

    @patch('lambda_functions.follow_user.boto3')
    @patch('lambda_functions.follow_user.datatier')
    def test_blocked_by_user(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({
                'host': 'test_host',
                'port': 3306,
                'username': 'test_user',
                'password': 'test_password'
            })
        }
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls
        mock_datatier.retrieve_all_rows.side_effect = [
            [('follower_id',)], # Follower exists
            [('followee_id',)], # Followee exists
            [], # Not already following
            [('followee_id', 'follower_id')] # Is blocked
        ]

        event = {
            'body': json.dumps({
                'follower': 'follower_id',
                'followee_username': 'followee_username'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 403)
        self.assertEqual(json.loads(response['body'])['message'], 'Cannot follow user: you have been blocked.')

    def test_missing_parameters(self):
        event = {'body': json.dumps({})}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('missing', json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()