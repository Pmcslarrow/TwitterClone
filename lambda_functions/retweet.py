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
    retweet.py
    --------------
    Receives:
        - The userid of who is retweeting
        - The postid of the post being retweeted
    
    On Success:
        - Adds a retweet to the Retweets table
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
            # Check if user exists
            check_user_sql = "SELECT userid FROM UserInfo WHERE userid = %s;"
            user_result = datatier.retrieve_all_rows(db_conn, check_user_sql, [userid])
            
            if not user_result:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "User does not exist."
                    })
                }
                
            # Check if post exists
            check_post_sql = "SELECT postid FROM PostInfo WHERE postid = %s;"
            post_result = datatier.retrieve_all_rows(db_conn, check_post_sql, [postid])
            
            if not post_result:
                return {
                    "statusCode": 404,
                    "body": json.dumps({
                        "message": "Post does not exist."
                    })
                }
            
            # Check if post author blocked the user
            check_blocked_sql = """
                SELECT b.blocker 
                FROM Blocked b 
                JOIN PostInfo p ON b.blocker = p.userid 
                WHERE b.blockee = %s AND p.postid = %s;
            """
            blocked_result = datatier.retrieve_all_rows(db_conn, check_blocked_sql, [userid, postid])
            
            if blocked_result:
                return {
                    "statusCode": 403,
                    "body": json.dumps({
                        "message": "Cannot retweet: you are blocked by the post author."
                    })
                }
                
            # Check if retweet already exists
            check_retweet_sql = "SELECT * FROM Retweets WHERE retweetuserid = %s AND originalpost = %s;"
            existing_retweet = datatier.retrieve_all_rows(db_conn, check_retweet_sql, [userid, postid])
            
            if existing_retweet:
                return {
                    "statusCode": 400,
            "headers": CORS_HEADERS,
                    "body": json.dumps({
                        "message": "You have already retweeted this post."
                    })
                }

            # Add retweet
            sql_statement = """
                INSERT INTO Retweets (retweetuserid, originalpost)
                VALUES (%s, %s);
            """

            datatier.perform_action(db_conn, sql_statement, [userid, postid])

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Successfully retweeted post."
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
                "message": f"An error occurred (retweet): {str(e)}"
            })
        }