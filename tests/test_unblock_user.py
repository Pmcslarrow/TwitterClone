import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.unblock_user import lambda_handler

class TestUnblockUser(unittest.TestCase):

    @patch('lambda_functions.unblock_user.boto3')
    @patch('lambda_functions.unblock_user.datatier')
    def test_unblock_user_success(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
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
            [('blockee_id',)],              # 1. Blockee user exists (lookup by username)
            [('blocker_id', 'blockee_id')]  # 2. Block relationship exists
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
        self.assertEqual(json.loads(response['body'])['message'], 'Successfully unblocked user.')
        mock_datatier.perform_action.assert_called_once()

    @patch('lambda_functions.unblock_user.boto3')
    @patch('lambda_functions.unblock_user.datatier')
    def test_unblock_nonexistent_relationship(self, mock_datatier, mock_boto3):
        # Mock Secrets Manager
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }

        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database calls to show no existing block
        mock_datatier.retrieve_all_rows.side_effect = [
            [('blockee_id',)],  # Blockee user exists
            []                  # Block relationship does NOT exist
        ]

        event = {
            'body': json.dumps({
                'blocker': 'blocker_id',
                'blockee_username': 'blockee_username'
            })
        }

        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body'])['message'], 'Block relationship does not exist.')
        mock_datatier.perform_action.assert_not_called()

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