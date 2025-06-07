from configparser import ConfigParser
import os
import json
import boto3
from datetime import datetime
import datatier

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

def lambda_handler(event, context):
    """
    Input:
    -----
    - userid -- The userid (email) of the user to check/create

    Logic:
    ------
    - Check if userid exists in database
    - If no: create new user with id, username, picture url, and placeholder bio
    - If yes: return the username, picture url, and bio
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

        if "userid" not in event_body:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"message": "userid missing."})
            }
        
        userid = event_body['userid']
        username = event_body.get('username', '')
        picture = event_body.get('picture', '')

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
            # Check if user exists
            sql = "SELECT username, picture, bio FROM UserInfo WHERE userid = %s;"
            rows = datatier.retrieve_all_rows(db_conn, sql, [userid])
            
            if rows:
                # User exists, return their info
                user_data = rows[0]
                return {
                    "statusCode": 200,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "username": user_data[0],
                        "picture": user_data[1],
                        "bio": user_data[2]
                    })
                }
            else:
                # User doesn't exist, create new user
                # Generate username from email if not provided
                if not username:
                    username = userid.split('@')[0]  # Use part before @ as username
                
                # Set default picture if not provided
                if not picture:
                    picture = "https://via.placeholder.com/150"
                
                placeholder_bio = "Biography!"
                
                insert_sql = "INSERT INTO UserInfo (userid, username, picture, bio) VALUES (%s, %s, %s, %s);"
                datatier.perform_action(db_conn, insert_sql, [userid, username, picture, placeholder_bio])
                
                return {
                    "statusCode": 200,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "username": username,
                        "picture": picture,
                        "bio": placeholder_bio,
                        "message": "New user created"
                    })
                }

        except Exception as e:
            print("Database operation ERR:", e)
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": f"An error occurred (user_profile): {str(e)}"
                })
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"An error occurred (user_profile): {str(e)}"
            })
        }