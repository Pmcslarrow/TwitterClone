import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.unretweet import lambda_handler

class TestUnretweet(unittest.TestCase):

    @patch('lambda_functions.unretweet.boto3')
    @patch('lambda_functions.unretweet.datatier')
    def test_unretweet_success(self, mock_datatier, mock_boto3):
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
        mock_datatier.retrieve_all_rows.return_value = [("user1", 20001)] # Retweet exists
        mock_datatier.perform_action.return_value = None
        
        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(json.loads(response["body"])["message"], "Successfully removed retweet.")

    @patch('lambda_functions.unretweet.boto3')
    @patch('lambda_functions.unretweet.datatier')
    def test_unretweet_nonexistent(self, mock_datatier, mock_boto3):
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
        mock_datatier.retrieve_all_rows.return_value = [] # Retweet does not exist
        
        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(json.loads(response["body"])["message"], "You have not retweeted this post.")

    def test_missing_userid(self):
        event = {'body': json.dumps({'postid': 20001})}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(json.loads(response["body"])["message"], "userid missing.")

if __name__ == '__main__':
    unittest.main()