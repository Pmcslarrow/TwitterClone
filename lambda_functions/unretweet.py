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
    unretweet.py
    --------------
    Receives:
        - The userid of who is removing the retweet
        - The postid of the post being unretweeted
    
    On Success:
        - Removes a retweet from the Retweets table
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

        # Establishing DB connection
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

        try:
            # Check if retweet exists
            check_retweet_sql = "SELECT * FROM Retweets WHERE retweetuserid = %s AND originalpost = %s;"
            existing_retweet = datatier.retrieve_all_rows(db_conn, check_retweet_sql, [userid, postid])
            
            if not existing_retweet:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "You have not retweeted this post."
                    })
                }

            # Remove retweet
            sql_statement = """
                DELETE FROM Retweets
                WHERE retweetuserid = %s AND originalpost = %s;
            """

            datatier.perform_action(db_conn, sql_statement, [userid, postid])

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "Successfully removed retweet."
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
                "message": f"An error occurred (unretweet): {str(e)}"
            })
        }