# INSERT INTO Likes (liker, originalpost)
# VALUES ('userid', postid);

from configparser import ConfigParser
import os
import datatier
import json
from datetime import datetime
import boto3


CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}



def lambda_handler(event, context):
    """
    
    delete_like.py
    --------------
    Receives:
        - The userid of who is unliking the post
        - The pageid of the post you are unliking
    
    On Success:
        - Removes a like from the Likes table 

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

        if "userid" not in event_body:
            return {
                "statusCode": 400,
                            "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "userid missing."
                })
            }
        
        if "postid" not in event_body:
            return {
                "statusCode": 400,
                            "headers": CORS_HEADERS,
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
            
            #
            # Checking to see if this userid and postid even exist in the Likes table
            #
            try:
                sql = "SELECT * FROM Likes WHERE liker = %s AND originalpost = %s"
                row = datatier.retrieve_all_rows(db_conn, sql, [userid, postid])

                if not row:
                    return {
                        "statusCode": 404,
                        "headers": CORS_HEADERS,
                                "body": json.dumps({
                            "message": "Like not found for given userid and postid."
                        })
                    }

            except Exception as e:
                print("Error checking Likes table:", str(e))
                return {
                    "statusCode": 500,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Failed to check Likes table due to server error."
                    })
                }

            sql_statement = """
                DELETE FROM Likes
                WHERE liker = %s AND originalpost = %s;
            """

            datatier.perform_action(db_conn, sql_statement, [userid, postid])

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": "Successfully removed like from the Likes table."
            }

        except Exception as e:
            print("Updating database ERR: ", e)

    except Exception as e:
        return {
            "statusCode": 400,
                        "headers": CORS_HEADERS,
                                "body": json.dumps({
                "message": f"An error occurred (delete_like): {str(e)}"
            })
        }