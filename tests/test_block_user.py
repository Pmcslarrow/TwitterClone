import unittest
import json
from unittest.mock import patch, MagicMock, call
from lambda_functions.block_user import lambda_handler

class TestBlockUser(unittest.TestCase):

    @patch('lambda_functions.block_user.boto3')
    @patch('lambda_functions.block_user.datatier')
    def test_block_user_success(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager for database credentials
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls
        mock_datatier.retrieve_all_rows.side_effect = [
            [('blocker_id',)],   # 1. Blocker exists
            [('blockee_id',)],   # 2. Blockee exists (lookup by username)
            []                   # 3. Not already blocked
        ]
        mock_datatier.perform_action.return_value = None

        # Prepare the test event
        event = {
            'body': json.dumps({
                'blocker': 'blocker_id',
                'blockee_username': 'blockee_username'
            })
        }

        # Call the lambda handler
        response = lambda_handler(event, None)

        # Assert the response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body'])['message'], 'Successfully blocked user.')

        # Verify that the insert and two deletes were called
        self.assertEqual(mock_datatier.perform_action.call_count, 3)

    @patch('lambda_functions.block_user.boto3')
    @patch('lambda_functions.block_user.datatier')
    def test_already_blocked(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls to show an existing block
        mock_datatier.retrieve_all_rows.side_effect = [
            [('blocker_id',)],
            [('blockee_id',)],
            [('blocker_id', 'blockee_id')]  # Block already exists
        ]

        event = {
            'body': json.dumps({
                'blocker': 'blocker_id',
                'blockee_username': 'blockee_username'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['message'], 'User is already blocked.')
        mock_datatier.perform_action.assert_not_called()

    def test_block_self(self):
        # This test doesn't need extensive mocks as it should fail before most DB interaction
        event = {
            'body': json.dumps({
                'blocker': 'user1',
                'blockee_username': 'user1'
            })
        }
        # We still need to mock the DB lookups that determine the user IDs are the same
        with patch('lambda_functions.block_user.boto3'), patch('lambda_functions.block_user.datatier') as mock_datatier:
            mock_datatier.retrieve_all_rows.side_effect = [
                [('user1',)], # Blocker exists
                [('user1',)]  # Blockee exists and has the same ID
            ]
            response = lambda_handler(event, None)
            self.assertEqual(response['statusCode'], 400)

    def test_missing_parameters(self):
        event_no_blocker = {'body': json.dumps({'blockee_username': 'user2'})}
        response_no_blocker = lambda_handler(event_no_blocker, None)
        self.assertEqual(response_no_blocker['statusCode'], 400)
        self.assertEqual(json.loads(response_no_blocker['body'])['message'], 'blocker userid missing.')

        event_no_blockee = {'body': json.dumps({'blocker': 'user1'})}
        response_no_blockee = lambda_handler(event_no_blockee, None)
        self.assertEqual(response_no_blockee['statusCode'], 400)
        self.assertEqual(json.loads(response_no_blockee['body'])['message'], 'blockee_username missing.')

if __name__ == '__main__':
    unittest.main()