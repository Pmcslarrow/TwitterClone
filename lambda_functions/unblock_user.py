## unblock_user.py

from configparser import ConfigParser
import os
try:
    import datatier
except:
    from . import datatier
import json
import boto3


CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}


def lambda_handler(event, context):
    """
    unblock_user.py
    --------------
    Receives:
        - The blocker userid (who is unblocking)
        - The blockee username (who is being unblocked)
    
    On Success:
        - Removes a block relationship from the Blocked table
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
        
        if "blockee_username" not in event_body:
            return {
                "statusCode": 400,
                            "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "blockee_username missing."
                })
            }
        
        blocker = event_body['blocker']
        blockee_username = event_body['blockee_username']

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
            # Get blockee userid from username
            check_blockee_sql = "SELECT userid FROM UserInfo WHERE username = %s;"
            blockee_result = datatier.retrieve_all_rows(db_conn, check_blockee_sql, [blockee_username])
            
            if not blockee_result:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Blockee user does not exist."
                    })
                }
            
            blockee = blockee_result[0][0]  # Extract userid from result
            
            # Check if block exists
            check_block_sql = "SELECT * FROM Blocked WHERE blocker = %s AND blockee = %s;"
            existing_block = datatier.retrieve_all_rows(db_conn, check_block_sql, [blocker, blockee])
            
            if not existing_block:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Block relationship does not exist."
                    })
                }

            # Remove block relationship
            sql_statement = """
                DELETE FROM Blocked
                WHERE blocker = %s AND blockee = %s;
            """

            datatier.perform_action(db_conn, sql_statement, [blocker, blockee])

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "Successfully unblocked user."
                })
            }

        except Exception as e:
            print("Database operation ERR: ", e)
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
                "message": f"An error occurred (unblock_user): {str(e)}"
            })
        }
