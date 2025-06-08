import unittest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from lambda_functions.get_recent_tweets import lambda_handler

class TestGetRecentTweets(unittest.TestCase):

    def setUp(self):
        """Set up common mock objects for each test."""
        # This is a sample row structure for timeline/reply posts (9 columns)
        self.mock_post_row = (
            20001,  # postid
            'user2',  # userid
            datetime(2024, 5, 10, 12, 30, 0),  # dateposted
            'This is a tweet from another user.',  # textcontent
            'pic2.jpg',  # picture
            None,  # reply_to_postid
            1,  # is_liked
            0,  # is_retweeted
            'User Two'  # username
        )
        # This is a sample row for user-specific posts (7 columns)
        self.mock_user_post_row = (
            20002, # postid
            'user3', # userid
            datetime(2024, 5, 11, 1, 0, 0), # dateposted
            'A post from a specific profile.', # textcontent
            'pic3.jpg', # picture
            None, # reply_to_postid
            'User Three' # username
        )

    @patch('lambda_functions.get_recent_tweets.boto3')
    @patch('lambda_functions.get_recent_tweets.datatier')
    def test_get_timeline_success(self, mock_datatier, mock_boto3):
        """Tests successfully fetching a user's main timeline."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        mock_datatier.retrieve_all_rows.return_value = [self.mock_post_row]

        # Event for a general timeline fetch
        event = {"body": json.dumps({"userid": "user1"})}
        
        response = lambda_handler(event, None)
        
        # Assertions
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['post_id'], 20001)
        self.assertEqual(body[0]['username'], 'User Two')
        self.assertEqual(body[0]['liked'], 1)
        self.assertEqual(body[0]['retweeted'], 0)
        self.assertEqual(body[0]['dateposted'], '2024-05-10 12:30:00')

    @patch('lambda_functions.get_recent_tweets.boto3')
    @patch('lambda_functions.get_recent_tweets.datatier')
    def test_get_replies_success(self, mock_datatier, mock_boto3):
        """Tests successfully fetching replies for a specific post."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        mock_datatier.retrieve_all_rows.return_value = [self.mock_post_row]

        # Event to fetch replies for postid 20000
        event = {"body": json.dumps({"userid": "user1", "postid": 20000})}
        
        response = lambda_handler(event, None)
        
        # Assertions
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['post_id'], 20001)
        self.assertIn('liked', body[0]) # liked/retweeted fields should be present

    @patch('lambda_functions.get_recent_tweets.boto3')
    @patch('lambda_functions.get_recent_tweets.datatier')
    def test_get_user_posts_success(self, mock_datatier, mock_boto3):
        """Tests successfully fetching all posts for a specific user profile."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        mock_datatier.retrieve_all_rows.return_value = [self.mock_user_post_row]

        # Event to fetch posts from profile 'User Three'
        event = {"body": json.dumps({"userid": "user1", "profileUsername": "User Three"})}
        
        response = lambda_handler(event, None)
        
        # Assertions
        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['post_id'], 20002)
        self.assertEqual(body[0]['username'], 'User Three')
        # liked/retweeted fields should NOT be present for this query
        self.assertNotIn('liked', body[0])
        self.assertNotIn('retweeted', body[0])

    def test_missing_userid(self):
        """Tests that the lambda returns an error if userid is missing."""
        event = {"body": json.dumps({})}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(json.loads(response["body"])["message"], "userid missing.")

if __name__ == '__main__':
    unittest.main()