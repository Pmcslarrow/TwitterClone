from configparser import ConfigParser
import os
import datatier
import json
import boto3


CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}
 

def lambda_handler(event, context):
    """
    block_user.py
    --------------
    Receives:
        - The blocker userid (who is blocking)
        - The blockee userid (who is being blocked)
    
    On Success:
        - Adds a block relationship to the Blocked table
        - Removes any follower relationships between the users
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
        
        # Parse the body into a dictionary
        event_body = json.loads(event['body'])

        if "blocker" not in event_body:
            return {
                "statusCode": 400,
            "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "blocker userid missing."
                })
            }
        
        if "blockee" not in event_body:
            return {
                "statusCode": 400,
            "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "blockee userid missing."
                })
            }
        
        blocker = event_body['blocker']
        blockee = event_body['blockee']

        # Check if users are trying to block themselves
        if blocker == blockee:
            return {
                "statusCode": 400,
            "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "Users cannot block themselves."
                })
            }

        # Establishing DB connection
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
            # Check if users exist
            check_blocker_sql = "SELECT userid FROM UserInfo WHERE userid = %s;"
            blocker_result = datatier.retrieve_all_rows(db_conn, check_blocker_sql, [blocker])
            
            if not blocker_result:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "Blocker user does not exist."
                    })
                }
                
            check_blockee_sql = "SELECT userid FROM UserInfo WHERE userid = %s;"
            blockee_result = datatier.retrieve_all_rows(db_conn, check_blockee_sql, [blockee])
            
            if not blockee_result:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "Blockee user does not exist."
                    })
                }
                
            # Check if block already exists
            check_block_sql = "SELECT * FROM Blocked WHERE blocker = %s AND blockee = %s;"
            existing_block = datatier.retrieve_all_rows(db_conn, check_block_sql, [blocker, blockee])
            
            if existing_block:
                return {
                    "statusCode": 400,
            "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "message": "User is already blocked."
                    })
                }
            
            # Add block relationship
            block_sql = """
                INSERT INTO Blocked (blocker, blockee)
                VALUES (%s, %s);
            """
            datatier.perform_action(db_conn, block_sql, [blocker, blockee])

            # Remove any follower relationships in both directions
            remove_follows_sql1 = """
                DELETE FROM Followers
                WHERE follower = %s AND followee = %s;
            """
            datatier.perform_action(db_conn, remove_follows_sql1, [blockee, blocker])
            
            remove_follows_sql2 = """
                DELETE FROM Followers
                WHERE follower = %s AND followee = %s;
            """
            datatier.perform_action(db_conn, remove_follows_sql2, [blocker, blockee])

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Successfully blocked user."
                })
            }

        except Exception as e:
            print("Database operation ERR: ", e)
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "message": f"Database error: {str(e)}"
                })
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"An error occurred (block_user): {str(e)}"
            })
        }