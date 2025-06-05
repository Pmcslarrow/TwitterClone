from configparser import ConfigParser
import os
import json
import boto3


CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

from datetime import datetime
import datatier

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
            "content": row[3],
            "image_file_key": row[4],
            "reply_to_postid": row[5],
            "is_liked": bool(row[6]),
            "is_retweeted": bool(row[7])
        })
    return serialized

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

def lambda_handler(event, context):
    """
    
    get_recent_tweets
    --------------
    Receives:
        - The userid PK to identify the user who is scrolling through the tweets (we need to find the tweets that either belong to the user or were posted by users they follow
    
    On Success:
        - Returns a list of all "recent tweets" with like and retweet status

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
                                "body": json.dumps({"message": "userid missing."})
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
                SELECT DISTINCT 
                    p.postid,
                    p.userid,
                    p.dateposted,
                    p.textcontent,
                    p.image_file_key,
                    p.reply_to_postid,
                    CASE WHEN l.liker IS NOT NULL THEN 1 ELSE 0 END AS is_liked,
                    CASE WHEN r.retweetuserid IS NOT NULL THEN 1 ELSE 0 END AS is_retweeted
                FROM PostInfo p
                LEFT JOIN Followers f ON p.userid = f.followee
                LEFT JOIN Likes l ON p.postid = l.originalpost AND l.liker = %s
                LEFT JOIN Retweets r ON p.postid = r.originalpost AND r.retweetuserid = %s
                WHERE f.follower = %s OR p.userid = %s
                ORDER BY p.dateposted DESC
                LIMIT 500;
            """

            rows = datatier.retrieve_all_rows(db_conn, sql_statement, [userid, userid, userid, userid])
           
            print("Rows retrieved: ", rows)

            serialized_rows = serialize_rows(rows)

            return {
                "statusCode": 200,
                                "headers": CORS_HEADERS,
                                "body": json.dumps(serialized_rows)
            }

        except Exception as e:
            print("Updating database ERR: ", e)
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