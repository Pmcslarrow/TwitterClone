import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.follow_user import lambda_handler

class TestFollowUser(unittest.TestCase):
    @patch('lambda_functions.follow_user.datatier')
    @patch('lambda_functions.follow_user.ConfigParser')
    def test_follow_user_success(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows for user existence checks
        mock_datatier.retrieve_all_rows.side_effect = [
            [{"userid": "user1"}],  # follower exists
            [{"userid": "user2"}],  # followee exists
            [],                     # relationship doesn't exist yet
            []                      # not blocked
        ]
        
        # Mock perform_action for insertion
        mock_datatier.perform_action.return_value = None
        
        # Create test event
        event = {
            "body": json.dumps({
                "follower": "user1",
                "followee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 200)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Successfully followed user.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 4)
        mock_datatier.perform_action.assert_called_once()

    @patch('lambda_functions.follow_user.datatier')
    @patch('lambda_functions.follow_user.ConfigParser')
    def test_follow_already_following(self, mock_config, mock_datatier):
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
            [{"userid": "user1"}],                  # follower exists
            [{"userid": "user2"}],                  # followee exists
            [{"follower": "user1", "followee": "user2"}]  # relationship already exists
        ]
        
        # Create test event
        event = {
            "body": json.dumps({
                "follower": "user1",
                "followee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User is already following this account.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 3)
        mock_datatier.perform_action.assert_not_called()

    @patch('lambda_functions.follow_user.datatier')
    @patch('lambda_functions.follow_user.ConfigParser')
    def test_follow_blocked_user(self, mock_config, mock_datatier):
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
            [{"userid": "user1"}],  # follower exists
            [{"userid": "user2"}],  # followee exists
            [],                     # relationship doesn't exist yet
            [{"blocker": "user2", "blockee": "user1"}]  # user is blocked
        ]
        
        # Create test event
        event = {
            "body": json.dumps({
                "follower": "user1",
                "followee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Cannot follow user: you have been blocked.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 4)
        mock_datatier.perform_action.assert_not_called()

    @patch('lambda_functions.follow_user.datatier')
    @patch('lambda_functions.follow_user.ConfigParser')
    def test_follow_nonexistent_follower(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows for user existence checks - follower doesn't exist
        mock_datatier.retrieve_all_rows.return_value = []
        
        # Create test event
        event = {
            "body": json.dumps({
                "follower": "nonexistent_user",
                "followee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Follower user does not exist.")
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_not_called()

    def test_follow_missing_body(self):
        # Create test event with no body
        event = {}
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User error. No data received.")

    def test_follow_missing_follower(self):
        # Create test event with missing follower field
        event = {
            "body": json.dumps({
                "followee": "user2"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "follower userid missing.")

    def test_follow_missing_followee(self):
        # Create test event with missing followee field
        event = {
            "body": json.dumps({
                "follower": "user1"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "followee userid missing.")

    def test_follow_self(self):
        # Create test event with same follower and followee
        event = {
            "body": json.dumps({
                "follower": "user1",
                "followee": "user1"
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Users cannot follow themselves.")

if __name__ == '__main__':
    unittest.main()