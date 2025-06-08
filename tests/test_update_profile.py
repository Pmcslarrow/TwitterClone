import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.update_profile import lambda_handler

class TestUpdateProfile(unittest.TestCase):

    @patch('lambda_functions.update_profile.boto3')
    @patch('lambda_functions.update_profile.datatier')
    def test_successful_full_update(self, mock_datatier, mock_boto3):
        """Tests updating all possible profile fields at once."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        mock_datatier.perform_action.return_value = None

        # Prepare event with all updateable fields
        event = {
            "body": json.dumps({
                "userid": "123",
                "bio": "Updated bio",
                "username": "updated_user",
                "picture": "updated_picture_url"
            })
        }

        response = lambda_handler(event, None)

        # Assert a successful response
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(json.loads(response["body"])["message"], "Profile updated successfully.")

        # Verify the dynamically generated SQL and parameters are correct
        # Note: The order of columns in the SET clause can vary, so we check the components.
        args, kwargs = mock_datatier.perform_action.call_args
        self.assertIn("UPDATE UserInfo", args[1])
        self.assertIn("SET", args[1])
        self.assertIn("bio = %s", args[1])
        self.assertIn("username = %s", args[1])
        self.assertIn("picture = %s", args[1])
        self.assertIn("WHERE userid = %s", args[1])
        self.assertIn("123", args[2]) # Check that the userid is the last parameter

    @patch('lambda_functions.update_profile.boto3')
    @patch('lambda_functions.update_profile.datatier')
    def test_successful_partial_update(self, mock_datatier, mock_boto3):
        """Tests updating only a single profile field."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        mock_datatier.perform_action.return_value = None

        # Event with only 'bio' being updated
        event = {"body": json.dumps({"userid": "123", "bio": "New bio only"})}
        
        response = lambda_handler(event, None)

        # Assert success
        self.assertEqual(response["statusCode"], 200)

        # Verify SQL is correct for a single field update
        expected_sql = "\n                UPDATE UserInfo\n                SET bio = %s\n                WHERE userid = %s;\n            "
        expected_params = ["New bio only", "123"]
        mock_datatier.perform_action.assert_called_once_with(mock_conn, expected_sql, expected_params)

    def test_failure_missing_userid(self):
        """Tests that the function fails correctly if userid is missing."""
        # This test doesn't need mocks as it fails before DB connection
        event = {"body": json.dumps({"bio": "bio without user"})}
        
        response = lambda_handler(event, None)
        
        # Assert a 400 Bad Request response
        self.assertEqual(response["statusCode"], 400)
        self.assertIn("userid missing", json.loads(response["body"])["message"])

    @patch('lambda_functions.update_profile.boto3')
    @patch('lambda_functions.update_profile.datatier')
    def test_ignores_empty_string_values(self, mock_datatier, mock_boto3):
        """Tests that empty strings are ignored and not included in the update."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Event with a valid bio but an empty username
        event = {"body": json.dumps({"userid": "123", "bio": "A valid bio", "username": ""})}
        
        lambda_handler(event, None)
        
        # Assert that only the 'bio' field was included in the SQL
        expected_sql = "\n                UPDATE UserInfo\n                SET bio = %s\n                WHERE userid = %s;\n            "
        expected_params = ["A valid bio", "123"]
        mock_datatier.perform_action.assert_called_once_with(mock_conn, expected_sql, expected_params)

if __name__ == '__main__':
    unittest.main()