from configparser import ConfigParser
import os
import json
import boto3
from datetime import datetime
try:
    import datatier
except:
    from . import datatier

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

def lambda_handler(event, context):
    """
    Input:
    -----
    - current_userid : The userid of the current user (potential follower/blocker)
    - username : The username of the profile information you want to receive 

    Output: 
    ------
    - Returns profile info (bio, picture) and relationship status (is_following, is_blocked)
    """
    try:
        if "body" not in event:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "User error. No data received."
                })
            }
        
        event_body = json.loads(event['body'])

        if "current_userid" not in event_body:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "current_userid missing."})
            }

        if "username" not in event_body:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "username missing."})
            }
        
        current_userid = event_body['current_userid']
        username = event_body['username']

        # Establish DB connection
        secret_manager = boto3.client('secretsmanager')
        secret_name = "prod/twitterclone/sql"
        secret = json.loads(secret_manager.get_secret_value(SecretId=secret_name)['SecretString'])
        rds_endpoint = secret['host']
        rds_portnum = secret['port']
        rds_username = secret['username']
        rds_pwd = secret['password']
        rds_dbname = "TwitterClone"

        db_conn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        try:
            # Get profile info
            profile_sql = "SELECT userid, bio, picture FROM UserInfo WHERE username = %s;"
            profile_row = datatier.retrieve_one_row(db_conn, profile_sql, [username])
            
            if not profile_row:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"message": "User not found."})
                }
            
            target_userid, bio, picture = profile_row
            
            # Check if current user follows this user
            follow_sql = "SELECT 1 FROM Followers WHERE follower = %s AND followee = %s;"
            is_following = bool(datatier.retrieve_one_row(db_conn, follow_sql, [current_userid, target_userid]))
            
            # Check if current user blocks this user
            block_sql = "SELECT 1 FROM Blocked WHERE blocker = %s AND blockee = %s;"
            is_blocked = bool(datatier.retrieve_one_row(db_conn, block_sql, [current_userid, target_userid]))
            
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "bio": bio,
                    "picture": picture,
                    "is_following": is_following,
                    "is_blocked": is_blocked
                })
            }

        except Exception as e:
            print("Database operation ERR:", e)
            return {
                "statusCode": 500,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": f"Database error: {str(e)}"
                })
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"An error occurred: {str(e)}"
            })
        }