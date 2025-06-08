import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.retweet import lambda_handler

class TestRetweet(unittest.TestCase):

    @patch('lambda_functions.retweet.boto3')
    @patch('lambda_functions.retweet.datatier')
    def test_retweet_success(self, mock_datatier, mock_boto3):
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
            [('user1',)],  # user exists
            [('20001',)],  # post exists
            [],            # not blocked
            []             # no existing retweet
        ]
        mock_datatier.perform_action.return_value = None
        
        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(json.loads(response["body"])["message"], "Successfully retweeted post.")

    @patch('lambda_functions.retweet.boto3')
    @patch('lambda_functions.retweet.datatier')
    def test_already_retweeted(self, mock_datatier, mock_boto3):
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
            [('user1',)],  # user exists
            [('20001',)],  # post exists
            [],            # not blocked
            [('user1', 20001)]  # retweet already exists
        ]
        
        event = {'body': json.dumps({'userid': 'user1', 'postid': 20001})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(json.loads(response["body"])["message"], "You have already retweeted this post.")

    def test_missing_userid(self):
        event = {'body': json.dumps({'postid': 20001})}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(json.loads(response["body"])["message"], "userid missing.")

if __name__ == '__main__':
    unittest.main()