# Post (Tweet)
# a. There should be a character limit on tweets

from configparser import ConfigParser
import os
from . import datatier
import json
import boto3


def lambda_handler(event, context):
    """
    
    Delete Post (Tweet)
    --------------
    Receives:
        - The postid PK to identify the post to delete
    
    On Success:
        - Removes tweet from PostInfo table

    """
    try:
        if "body" not in event:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "User error. No data received."
                })
            }
        
        # Parse the body into a dictionary
        event_body = json.loads(event['body'])
        
        if "postid" not in event_body:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "postid missing."
                })
            }
        
        postid = event_body['postid']

    
        print("Printing event object: ")
        print(event)
        print()


        #
        # Establishing DB connection
        #

        print("*** Establishing DB connection ***")

        secret_manager = boto3.client('secretsmanager')
        secret_name = "prod/twitterclone/sql"
        secret = json.loads(secret_manager.get_secret_value(SecretId=secret_name)['SecretString'])
        rds_endpoint = secret['host']
        rds_portnum = secret['port']
        rds_username = secret['username']
        rds_pwd = secret['password']
        rds_dbname = "TwitterClone"

        db_conn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)


        #
        # Making changes in database
        #
        try:
            sql_statement = """
                DELETE FROM PostInfo
                WHERE postid = %s;
            """
            datatier.perform_action(db_conn, sql_statement, [postid])

            print("Delete successful.")

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Post posted successfully."
                })
            }

        except Exception as e:
            print("Updating database ERR: ", e)

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"An error occurred (delete_tweet): {str(e)}"
            })
        }