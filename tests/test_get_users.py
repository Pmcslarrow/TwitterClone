import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.get_users import lambda_handler

class TestGetUsers(unittest.TestCase):

    @patch('lambda_functions.get_users.boto3')
    @patch('lambda_functions.get_users.datatier')
    def test_get_users_success(self, mock_datatier, mock_boto3):
        """Tests successfully retrieving a list of other users."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock the database response
        mock_user_list = [
            ('user2', 'UserTwo', 'pic2.jpg'),
            ('user3', 'UserThree', 'pic3.jpg')
        ]
        mock_datatier.retrieve_all_rows.return_value = mock_user_list
        
        event = {"body": json.dumps({"userid": "user1"})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(len(body), 2)
        
        # Verify the correct SQL was executed
        mock_datatier.retrieve_all_rows.assert_called_once_with(
            mock_conn,
            "SELECT userid, username, picture FROM UserInfo WHERE userid != %s;",
            ['user1']
        )

    def test_missing_userid(self):
        """Tests that the function fails if userid is missing."""
        event = {"body": json.dumps({})}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("userid missing", json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()