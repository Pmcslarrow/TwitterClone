# INSERT INTO Likes (liker, originalpost)
# VALUES ('userid', postid);

from configparser import ConfigParser
import os
import datatier
import json
from datetime import datetime
import boto3


def lambda_handler(event, context):
    """
    
    like_post.py
    --------------
    Receives:
        - The userid of who is liking the post
        - The pageid of the post being liked
    
    On Success:
        - Adds a like to the Likes table 

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

        if "userid" not in event_body:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "userid missing."
                })
            }
        
        if "postid" not in event_body:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "postid missing."
                })
            }
        
        userid = event_body['userid']
        postid = event_body['postid']


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
        # Adding Like to the Likes table
        #
        try:
            sql_statement = """
                INSERT INTO Likes (liker, originalpost)
                VALUES (%s, %s);
            """

            datatier.perform_action(db_conn, sql_statement, [userid, postid])

            return {
                "statusCode": 200,
                "body": "Successfully added like to the Likes table."
            }

        except Exception as e:
            print("Updating database ERR: ", e)

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"An error occurred (like_post): {str(e)}"
            })
        }