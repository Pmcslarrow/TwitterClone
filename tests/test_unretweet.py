import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.unretweet import lambda_handler

class TestUnretweet(unittest.TestCase):
    @patch('lambda_functions.unretweet.datatier')
    @patch('lambda_functions.unretweet.ConfigParser')
    def test_unretweet_success(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows for retweet check
        mock_datatier.retrieve_all_rows.return_value = [{"retweetuserid": "user1", "originalpost": 20001}]
        
        # Mock perform_action for deletion
        mock_datatier.perform_action.return_value = None
        
        # Create test event
        event = {
            "body": json.dumps({
                "userid": "user1",
                "postid": 20001
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Successfully removed retweet.")
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_called_once()

    @patch('lambda_functions.unretweet.datatier')
    @patch('lambda_functions.unretweet.ConfigParser')
    def test_unretweet_nonexistent_retweet(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - retweet doesn't exist
        mock_datatier.retrieve_all_rows.return_value = []
        
        # Create test event
        event = {
            "body": json.dumps({
                "userid": "user1",
                "postid": 20001
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "You have not retweeted this post.")
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_not_called()

    def test_unretweet_missing_body(self):
        # Create test event with no body
        event = {}
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User error. No data received.")

    def test_unretweet_missing_userid(self):
        # Create test event with missing userid field
        event = {
            "body": json.dumps({
                "postid": 20001
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "userid missing.")

    def test_unretweet_missing_postid(self):
        # Create test event with missing postid field
        event = {
            "body": json.dumps({
                "userid": "user1"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "postid missing.")

    @patch('lambda_functions.unretweet.datatier')
    @patch('lambda_functions.unretweet.ConfigParser')
    def test_unretweet_database_error(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - retweet exists
        mock_datatier.retrieve_all_rows.return_value = [{"retweetuserid": "user1", "originalpost": 20001}]
        
        # Mock perform_action to raise an exception
        mock_datatier.perform_action.side_effect = Exception("Database error")
        
        # Create test event
        event = {
            "body": json.dumps({
                "userid": "user1",
                "postid": 20001
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