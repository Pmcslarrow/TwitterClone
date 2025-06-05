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
    get_counts.py
    --------------
    Receives:
        - postids : An array of all postids we need to get the counts of
    
    On Success:
        - Returns an array of objects (or just objects)
          where anything that had values would return the 
          postid, like count, retweet count
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
        
        if "postids" not in event_body:
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "message": "postids missing."
                })
            }
        
        postids = event_body['postids']

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
            placeholders = ','.join(['%s'] * len(postids))
            sql = f'''
            SELECT originalpost, 
                CAST(SUM(likes_count) AS SIGNED) AS likes, 
                CAST(SUM(retweets_count) AS SIGNED) AS retweets
            FROM (
                SELECT originalpost, COUNT(*) AS likes_count, 0 AS retweets_count
                FROM Likes
                WHERE originalpost IN ({placeholders})
                GROUP BY originalpost

                UNION ALL

                SELECT originalpost, 0 AS likes_count, COUNT(*) AS retweets_count
                FROM Retweets
                WHERE originalpost IN ({placeholders})
                GROUP BY originalpost
            ) AS combined
            GROUP BY originalpost
            ORDER BY originalpost;
            '''
            
            params = postids + postids  # flatten it for both IN clauses
            rows = datatier.retrieve_all_rows(db_conn, sql, params)

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps(rows)
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
                "message": f"An error occurred (retweet): {str(e)}"
            })
        }

