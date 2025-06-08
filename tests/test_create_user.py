import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.create_user import lambda_handler

class TestCreateUser(unittest.TestCase):

    @patch('lambda_functions.create_user.boto3')
    @patch('lambda_functions.create_user.datatier')
    def test_create_new_user_success(self, mock_datatier, mock_boto3):
        """Tests successfully creating a new user."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Simulate that the user does not exist, then simulate a successful insert
        mock_datatier.retrieve_one_row.return_value = None
        mock_datatier.perform_action.return_value = 1  # 1 row affected

        event = {
            "body": json.dumps({
                "userid": "new_user@example.com",
                "username": "NewUser",
                "picture": "new_pic.jpg"
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        # The lambda returns an empty username on creation, which we test for
        self.assertEqual(body['username'], "")
        self.assertEqual(body['bio'], "This user hasn't written a bio yet.")
        mock_datatier.perform_action.assert_called_once()

    @patch('lambda_functions.create_user.boto3')
    @patch('lambda_functions.create_user.datatier')
    def test_get_existing_user_success(self, mock_datatier, mock_boto3):
        """Tests successfully retrieving an existing user's info."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Simulate that the user already exists
        existing_user_data = ('ExistingUser', 'existing_pic.jpg', 'A cool bio.')
        mock_datatier.retrieve_one_row.return_value = existing_user_data

        event = {
            "body": json.dumps({
                "userid": "existing_user@example.com",
                "username": "ExistingUser",
                "picture": "existing_pic.jpg"
            })
        }
        
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['username'], existing_user_data[0])
        self.assertEqual(body['picture'], existing_user_data[1])
        self.assertEqual(body['bio'], existing_user_data[2])
        # perform_action should not be called if the user exists
        mock_datatier.perform_action.assert_not_called()

    def test_missing_parameters(self):
        """Tests failure when required parameters are missing."""
        event = {"body": json.dumps({"username": "user", "picture": "pic"})}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("userid missing", json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()