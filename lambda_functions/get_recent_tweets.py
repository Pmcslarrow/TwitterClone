from configparser import ConfigParser
import os
import datatier
import json
import boto3
from datetime import datetime

def serialize_rows(rows):
    """
    Converts rows with datetime objects into JSON-serializable format.
    """
    serialized = []
    for row in rows:
        serialized.append({
            "post_id": row[0],
            "userid": row[1],
            "dateposted": row[2].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row[2], datetime) else row[2],
            "content": row[3]
        })
    return serialized



def lambda_handler(event, context):
    """
    
    get_recent_tweets
    --------------
    Receives:
        - The userid PK to identify the user who is scrolling through the tweets (we need to find the tweets that either belong to the user or were posted by users they follow
    
    On Success:
        - Returns a list of all "recent tweets"

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
        userid = event_body['userid']
    
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

        # print("PRINTING RDS INFO")
        # print(rds_endpoint, rds_username, rds_pwd, rds_dbname)

        db_conn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        #
        # Making changes in database
        #
        try:
            print("userid: ", userid)

            sql_statement = """
                SELECT DISTINCT p.*
                FROM PostInfo p
                LEFT JOIN Followers f ON p.userid = f.followee
                WHERE f.follower = %s OR p.userid = %s
                ORDER BY p.dateposted DESC
                LIMIT 500;
            """

            rows = datatier.retrieve_all_rows(db_conn, sql_statement, [userid, userid])
           
            print("Rows retrieved: ", rows)

            serialized_rows = serialize_rows(rows)

            return {
                "statusCode": 200,
                "body": json.dumps(serialized_rows)
            }

        except Exception as e:
            print("Updating database ERR: ", e)

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"An error occurred (recent_tweets): {str(e)}"
            })
        }