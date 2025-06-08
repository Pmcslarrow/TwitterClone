import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.get_counts import lambda_handler

class TestGetCounts(unittest.TestCase):

    @patch('lambda_functions.get_counts.boto3')
    @patch('lambda_functions.get_counts.datatier')
    def test_get_counts_success(self, mock_datatier, mock_boto3):
        """Tests successfully getting all counts for a list of post IDs."""
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock the return value of the UNION SQL query
        mock_db_rows = [
            (101, 'likes', 15, None),
            (102, 'likes', 1, None),
            (101, 'retweets', 7, None),
            (102, 'comments', 3, None)
        ]
        mock_datatier.retrieve_all_rows.return_value = mock_db_rows
        
        event = {"body": json.dumps({"postids": [101, 102]})}
        response = lambda_handler(event, None)
        
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        
        # Check that the response is structured correctly
        self.assertIn("likes", body)
        self.assertIn("retweets", body)
        self.assertIn("comment_counts", body)
        
        # Verify the counts
        self.assertEqual(len(body['likes']), 2)
        self.assertEqual(body['likes'][0]['like_count'], 15)
        self.assertEqual(len(body['retweets']), 1)
        self.assertEqual(body['retweets'][0]['retweet_count'], 7)
        self.assertEqual(len(body['comment_counts']), 1)
        self.assertEqual(body['comment_counts'][0]['comment_count'], 3)

    def test_empty_postid_list(self):
        """Tests that providing an empty list of postids returns empty counts."""
        event = {"body": json.dumps({"postids": []})}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        body = json.loads(response['body'])
        self.assertEqual(body['likes'], [])
        self.assertEqual(body['retweets'], [])
        self.assertEqual(body['comment_counts'], [])

    def test_missing_postids_key(self):
        """Tests failure when the postids key is missing."""
        event = {"body": json.dumps({})}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertIn("postids missing", json.loads(response['body'])['message'])

if __name__ == '__main__':
    unittest.main()