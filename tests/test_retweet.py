import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.retweet import lambda_handler

class TestRetweet(unittest.TestCase):
    @patch('lambda_functions.retweet.datatier')
    @patch('lambda_functions.retweet.ConfigParser')
    def test_retweet_success(self, mock_config, mock_datatier):
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
            [{"userid": "user1"}],  # user exists
            [{"postid": 20001}],    # post exists
            [],                     # user not blocked
            []                      # no existing retweet
        ]
        
        # Mock perform_action for insertion
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
        self.assertEqual(response_body["message"], "Successfully retweeted post.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 4)
        mock_datatier.perform_action.assert_called_once()

    @patch('lambda_functions.retweet.datatier')
    @patch('lambda_functions.retweet.ConfigParser')
    def test_retweet_already_retweeted(self, mock_config, mock_datatier):
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
            [{"userid": "user1"}],                     # user exists
            [{"postid": 20001}],                       # post exists
            [],                                        # user not blocked
            [{"retweetuserid": "user1", "originalpost": 20001}]  # retweet already exists
        ]
        
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
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "You have already retweeted this post.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 4)
        mock_datatier.perform_action.assert_not_called()

    @patch('lambda_functions.retweet.datatier')
    @patch('lambda_functions.retweet.ConfigParser')
    def test_retweet_blocked_user(self, mock_config, mock_datatier):
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
            [{"userid": "user1"}],  # user exists
            [{"postid": 20001}],    # post exists
            [{"blocker": "user2"}]  # user is blocked
        ]
        
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
        self.assertEqual(response["statusCode"], 403)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Cannot retweet: you are blocked by the post author.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 3)
        mock_datatier.perform_action.assert_not_called()

    @patch('lambda_functions.retweet.datatier')
    @patch('lambda_functions.retweet.ConfigParser')
    def test_retweet_nonexistent_user(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - user doesn't exist
        mock_datatier.retrieve_all_rows.return_value = []
        
        # Create test event
        event = {
            "body": json.dumps({
                "userid": "nonexistent_user",
                "postid": 20001
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User does not exist.")
        
        # Verify database calls
        mock_datatier.retrieve_all_rows.assert_called_once()
        mock_datatier.perform_action.assert_not_called()

    @patch('lambda_functions.retweet.datatier')
    @patch('lambda_functions.retweet.ConfigParser')
    def test_retweet_nonexistent_post(self, mock_config, mock_datatier):
        # Setup for the mock ConfigParser
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.read.return_value = None
        mock_config_instance.get.side_effect = ["endpoint", "3306", "username", "password", "dbname"]
        
        # Setup mock database connection
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock retrieve_all_rows - user exists but post doesn't
        mock_datatier.retrieve_all_rows.side_effect = [
            [{"userid": "user1"}],  # user exists
            []                      # post doesn't exist
        ]
        
        # Create test event
        event = {
            "body": json.dumps({
                "userid": "user1",
                "postid": 99999
            })
        }
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 404)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "Post does not exist.")
        
        # Verify database calls
        self.assertEqual(mock_datatier.retrieve_all_rows.call_count, 2)
        mock_datatier.perform_action.assert_not_called()

    def test_retweet_missing_body(self):
        # Create test event with no body
        event = {}
        
        # Call the lambda handler
        response = lambda_handler(event, None)
        
        # Assert the response
        self.assertEqual(response["statusCode"], 400)
        response_body = json.loads(response["body"])
        self.assertEqual(response_body["message"], "User error. No data received.")

    def test_retweet_missing_userid(self):
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

    def test_retweet_missing_postid(self):
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

if __name__ == '__main__':
    unittest.main()