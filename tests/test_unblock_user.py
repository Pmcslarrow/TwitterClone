import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.unblock_user import lambda_handler

class TestUnblockUser(unittest.TestCase):
    @patch('lambda_functions.unblock_user.datatier')
    @patch('lambda_functions.unblock_user.ConfigParser')
    def test_unblock_user_success(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows for block check
        mock_datatier.retrieve_all_rows.return_value = [{"blocker": "user1", "blockee": "user2"}]
        
        # Mock perform_action for deletion
        mock_datatier.perform_action.return_value = None
        
        # Create test event
        event = {
            "body": json.dumps({
                "blocker": "user1",
                "blockee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Successfully unblocked user.")
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_called_once()

    @patch('lambda_functions.unblock_user.datatier')
    @patch('lambda_functions.unblock_user.ConfigParser')
    def test_unblock_nonexistent_block(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - block doesn't exist
        mock_datatier.retrieve_all_rows.return_value = []
        
        # Create test event
        event = {
            "body": json.dumps({
                "blocker": "user1",
                "blockee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Block relationship does not exist.")
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_not_called()

    def test_unblock_missing_body(self):
        # Create test event with no body
        event = {}
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User error. No data received.")

    def test_unblock_missing_blocker(self):
        # Create test event with missing blocker field
        event = {
            "body": json.dumps({
                "blockee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "blocker userid missing.")

    def test_unblock_missing_blockee(self):
        # Create test event with missing blockee field
        event = {
            "body": json.dumps({
                "blocker": "user1"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "blockee userid missing.")

    @patch('lambda_functions.unblock_user.datatier')
    @patch('lambda_functions.unblock_user.ConfigParser')
    def test_unblock_database_error(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - block exists
        mock_datatier.retrieve_all_rows.return_value = [{"blocker": "user1", "blockee": "user2"}]
        
        # Mock perform_action to raise an exception
        mock_datatier.perform_action.side_effect = Exception("Database error")
        
        # Create test event
        event = {
            "body": json.dumps({
                "blocker": "user1",
                "blockee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 500)
        response_body = json.loads(response["body"])
        self.assertTrue("Database error" in response_body["message"])
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_called_once()

if __name__ == '__main__':
    unittest.main()