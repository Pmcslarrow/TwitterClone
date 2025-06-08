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

def get_all_counts_union(db_conn, postids):
    placeholders = ','.join(['%s'] * len(postids))
    
    sql = f'''
        SELECT originalpost as postid, 'likes' as type, COUNT(*) as count, NULL as comment_id
        FROM Likes 
        WHERE originalpost IN ({placeholders})
        GROUP BY originalpost
        
        UNION ALL
        
        SELECT originalpost as postid, 'retweets' as type, COUNT(*) as count, NULL as comment_id
        FROM Retweets 
        WHERE originalpost IN ({placeholders})
        GROUP BY originalpost
        
        UNION ALL
        
        SELECT reply_to_postid as postid, 'comments' as type, COUNT(*) as count, NULL as comment_id
        FROM PostInfo 
        WHERE reply_to_postid IN ({placeholders})
        GROUP BY reply_to_postid
    '''
    
    rows = datatier.retrieve_all_rows(db_conn, sql, postids * 3)
    
    # Organize results by type
    likes = [{"originalpost": row[0], "like_count": row[2]} 
             for row in rows if row[1] == 'likes']
    retweets = [{"originalpost": row[0], "retweet_count": row[2]} 
                for row in rows if row[1] == 'retweets']
    comment_counts = [{"reply_to_postid": row[0], "comment_count": row[2]} 
                      for row in rows if row[1] == 'comments']

    return likes, retweets, comment_counts

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

        if not postids:  # Check for empty list
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps({
                    "likes": [],
                    "retweets": [],
                    "comment_counts": []
                })
            }

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
            likes, retweets, comment_counts = get_all_counts_union(db_conn, postids)

            print(f"Likes: {likes}")
            print(f"Retweets: {retweets}")
            print(f"Comment counts: {comment_counts}")

            response_data = {
                "likes": likes,
                "retweets": retweets,
                "comment_counts": comment_counts,
            }

            return {
                "statusCode": 200,
                                "headers": CORS_HEADERS,
                                "body": json.dumps(response_data)
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