import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.block_user import lambda_handler

class TestBlockUser(unittest.TestCase):
    @patch('lambda_functions.block_user.datatier')
    @patch('lambda_functions.block_user.ConfigParser')
    def test_block_user_success(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows for checks
        mock_datatier.retrieve_all_rows.side_effect = [
            [{"userid": "user1"}],  # blocker exists
            [{"userid": "user2"}],  # blockee exists
            []                      # block doesn't exist yet
        ]
        
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
        self.assertEqual(response_body["message"], "Successfully blocked user.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 3)
        self.assertEqual(mock_datatier.perform_action.call_count, 3)  # 1 for block + 2 for follow relationships
        mock_conn.start_transaction.assert_called_once()
        mock_conn.commit.assert_called_once()

    @patch('lambda_functions.block_user.datatier')
    @patch('lambda_functions.block_user.ConfigParser')
    def test_block_already_blocked(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows for checks
        mock_datatier.retrieve_all_rows.side_effect = [
            [{"userid": "user1"}],               # blocker exists
            [{"userid": "user2"}],               # blockee exists
            [{"blocker": "user1", "blockee": "user2"}]  # block already exists
        ]
        
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
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User is already blocked.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 3)
        mock_datatier.perform_action.assert_not_called()
        mock_conn.start_transaction.assert_not_called()

    @patch('lambda_functions.block_user.datatier')
    @patch('lambda_functions.block_user.ConfigParser')
    def test_block_nonexistent_blocker(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - blocker doesn't exist
        mock_datatier.retrieve_all_rows.return_value = []
        
        # Create test event
        event = {
            "body": json.dumps({
                "blocker": "nonexistent_user",
                "blockee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Blocker user does not exist.")
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_not_called()
        mock_conn.start_transaction.assert_not_called()

    @patch('lambda_functions.block_user.datatier')
    @patch('lambda_functions.block_user.ConfigParser')
    def test_block_nonexistent_blockee(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - blocker exists but blockee doesn't
        mock_datatier.retrieve_all_rows.side_effect = [
            [{"userid": "user1"}],  # blocker exists
            []                      # blockee doesn't exist
        ]
        
        # Create test event
        event = {
            "body": json.dumps({
                "blocker": "user1",
                "blockee": "nonexistent_user"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Blockee user does not exist.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 2)
        mock_datatier.perform_action.assert_not_called()
        mock_conn.start_transaction.assert_not_called()

    def test_block_missing_body(self):
        # Create test event with no body
        event = {}
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User error. No data received.")

    def test_block_missing_blocker(self):
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

    def test_block_missing_blockee(self):
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

    def test_block_self(self):
        # Create test event with same blocker and blockee
        event = {
            "body": json.dumps({
                "blocker": "user1",
                "blockee": "user1"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Users cannot block themselves.")

    @patch('lambda_functions.block_user.datatier')
    @patch('lambda_functions.block_user.ConfigParser')
    def test_block_database_error(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows for checks
        mock_datatier.retrieve_all_rows.side_effect = [
            [{"userid": "user1"}],  # blocker exists
            [{"userid": "user2"}],  # blockee exists
            []                      # block doesn't exist yet
        ]
        
        # Mock start_transaction and perform_action to raise an exception
        mock_conn.start_transaction.return_value = None
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
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 3)
        mock_datatier.perform_action.assert_called_once()
        mock_conn.start_transaction.assert_called_once()
        mock_conn.rollback.assert_called_once()

if __name__ == '__main__':
    unittest.main()