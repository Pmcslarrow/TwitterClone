from configparser import ConfigParser
import os
from . import datatier
import json
import boto3

def lambda_handler(event, context):
    """
    unblock_user.py
    --------------
    Receives:
        - The blocker userid (who is unblocking)
        - The blockee userid (who is being unblocked)
    
    On Success:
        - Removes a block relationship from the Blocked table
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

        if "blocker" not in event_body:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "blocker userid missing."
                })
            }
        
        if "blockee" not in event_body:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "blockee userid missing."
                })
            }
        
        blocker = event_body['blocker']
        blockee = event_body['blockee']

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
            # Check if block exists
            check_block_sql = "SELECT * FROM Blocked WHERE blocker = %s AND blockee = %s;"
            existing_block = datatier.retrieve_all_rows(db_conn, check_block_sql, [blocker, blockee])
            
            if not existing_block:
                return {
                    "statusCode": 404,
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
                "body": json.dumps({
                    "message": "Successfully unblocked user."
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
            "body": json.dumps({
                "message": f"An error occurred (unblock_user): {str(e)}"
            })
        }