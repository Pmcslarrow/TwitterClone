import unittest
import json
from unittest.mock import patch, MagicMock
from lambda_functions.delete_post import lambda_handler

class TestDeletePost(unittest.TestCase):

    @patch('lambda_functions.delete_post.boto3')
    @patch('lambda_functions.delete_post.datatier')
    def test_successful_post_deletion(self, mock_datatier, mock_boto3):
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn

        # Mock database checks to show the post exists
        mock_datatier.retrieve_one_row.return_value = (1,) # Simulate finding the post
        mock_datatier.perform_action.return_value = None

        # Create a valid event
        event = {"body": json.dumps({"postid": "1"})}
        response = lambda_handler(event, None)
        
        # Assert the response is successful
        self.assertEqual(response["statusCode"], 200)
        # Note: The success message in the lambda seems to be a copy-paste error.
        # The test is written to match the current lambda code.
        self.assertEqual(json.loads(response["body"])["message"], "Post posted successfully.")
        
        # Verify the delete action was called
        mock_datatier.perform_action.assert_called_once_with(
            mock_conn,
            "\n                DELETE FROM PostInfo\n                WHERE postid = %s;\n            ",
            ['1']
        )

    @patch('lambda_functions.delete_post.boto3')
    @patch('lambda_functions.delete_post.datatier')
    def test_delete_non_existent_postid(self, mock_datatier, mock_boto3):
        # Mock dependencies
        mock_secrets_manager = MagicMock()
        mock_boto3.client.return_value = mock_secrets_manager
        mock_secrets_manager.get_secret_value.return_value = {
            'SecretString': json.dumps({'host': 'h', 'port': 1, 'username': 'u', 'password': 'p'})
        }
        mock_conn = MagicMock()
        mock_datatier.get_dbConn.return_value = mock_conn
        
        # Mock database check to show the post does NOT exist
        mock_datatier.retrieve_one_row.return_value = None

        # Create event with a non-existent postid
        event = {"body": json.dumps({"postid": "999"})}
        response = lambda_handler(event, None)

        # Assert a 404 Not Found response
        self.assertEqual(response["statusCode"], 404)
        self.assertEqual(json.loads(response["body"])["message"], "Post with postid 999 does not exist.")
        
        # Verify that the delete action was never called
        mock_datatier.perform_action.assert_not_called()

    def test_missing_postid(self):
        # This test doesn't need mocks
        event = {"body": json.dumps({})}
        response = lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(json.loads(response["body"])["message"], "postid missing.")

if __name__ == '__main__':
    unittest.main()