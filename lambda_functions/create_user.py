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
    - userid -- The userid (email) of the user
    - username -- The username for the user
    - picture -- The picture URL for the user

    Logic:
    ------
    - Check if userid exists in database
    - If no: create new user with id, username, picture url, and placeholder bio
    - If yes: return existing username, picture url, and bio
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

        # Validate required fields
        required_fields = ["userid", "username", "picture"]
        for field in required_fields:
            if field not in event_body:
                return {
                    "statusCode": 400,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({"message": f"{field} missing."})
                }
        
        userid = event_body['userid']
        username = event_body['username']
        picture = event_body['picture']

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
            check_sql = "SELECT username, picture, bio FROM UserInfo WHERE userid = %s;"
            existing_user = datatier.retrieve_one_row(db_conn, check_sql, [userid])
            
            if existing_user:
                # User exists, return their info
                return {
                    "statusCode": 200,
                    "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "username": existing_user[0],
                        "picture": existing_user[1],
                        "bio": existing_user[2] if existing_user[2] else "This user hasn't written a bio yet."
                    })
                }
            else:
                # User doesn't exist, create new user
                placeholder_bio = "This user hasn't written a bio yet."
                insert_sql = "INSERT INTO UserInfo (userid, username, picture, bio) VALUES (%s, %s, %s, %s);"
                
                rows_affected = datatier.perform_action(db_conn, insert_sql, [userid, username, picture, placeholder_bio])
                
                if rows_affected > 0:
                    return {
                        "statusCode": 201,
                        "headers": CORS_HEADERS,
                        "body": json.dumps({
                            "username": username,
                            "picture": picture,
                            "bio": placeholder_bio,
                            "message": "New user created successfully."
                        })
                    }
                else:
                    return {
                        "statusCode": 400,
                        "headers": CORS_HEADERS,
                        "body": json.dumps({
                            "message": "Failed to create new user."
                        })
                    }

        except Exception as e:
            print("Database operation ERR:", e)
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": f"An error occurred (user_management): {str(e)}"
                })
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"An error occurred (user_management): {str(e)}"
            })
        }