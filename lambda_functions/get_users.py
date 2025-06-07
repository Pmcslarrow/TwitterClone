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
    - userid -- The userid of the user that is logged in, so that we don't get their information accidentally. 

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
            sql = "SELECT (userid, username) FROM UserInfo WHERE userid != %s;"
            rows = datatier.retrieve_all_rows(db_conn, sql, [userid])
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps(rows)
            }

        except Exception as e:
            print("Updating database ERR:", e)
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": f"An error occurred (recent_tweets): {str(e)}"
                })
            }

    except Exception as e:
        return {
            "statusCode": 400,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "message": f"An error occurred (recent_tweets): {str(e)}"
            })
        }