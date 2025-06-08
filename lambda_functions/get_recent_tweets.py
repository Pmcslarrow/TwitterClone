from configparser import ConfigParser
import os
import json
import boto3
from datetime import datetime
try:
    import datatier
except:
    from . import datatier

CORS_HEADERS = {
   'Access-Control-Allow-Origin': '*',
   'Access-Control-Allow-Headers': 'Content-Type',
   'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

def serialize_rows(rows, include_likes_retweets=True):
   """
   Converts rows with datetime objects into JSON-serializable format.
   If include_likes_retweets is False, skips those fields.
   """
   serialized = []
   for row in rows:
       print(row)
       base = {
           "post_id": row[0],
           "userid": row[1],
           "dateposted": row[2].strftime('%Y-%m-%d %H:%M:%S') if isinstance(row[2], datetime) else row[2],
           "content": row[3],
           "image": row[4],
           "username": row[8] if include_likes_retweets else row[6],
       }

       if include_likes_retweets:
           base["liked"] = row[6]
           base["retweeted"] = row[7]

       serialized.append(base)

   return serialized


def lambda_handler(event, context):
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
       postid = event_body.get('postid', None)  # Optional
       profileUsername = event_body.get('profileUsername', None)  # Optional - NEW

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
           print("userid:", userid)
           print("postid:", postid)
           print("username:", profileUsername)

           if profileUsername is not None:
               # Fetch root posts from a specific user by username - NEW
               print(f"Fetching root posts from user: {profileUsername}")
               sql_statement = """
                   SELECT
                       p.postid,
                       p.userid,
                       p.dateposted,
                       p.textcontent,
                       u.picture,
                       p.reply_to_postid,
                       u.username
                   FROM PostInfo p
                   JOIN UserInfo u ON p.userid = u.userid
                   LEFT JOIN Blocked b ON p.userid = b.blockee AND b.blocker = %s
                   WHERE u.username = %s AND p.reply_to_postid IS NULL AND b.blockee IS NULL
                   ORDER BY p.dateposted DESC
               """
               rows = datatier.retrieve_all_rows(db_conn, sql_statement, [userid, profileUsername])
               serialized_rows = serialize_rows(rows, include_likes_retweets=False)
           elif postid is not None:
               # Fetch replies to a specific post
               print(f"Checking to see if {userid} liked post {postid}")
               sql_statement = """
                  SELECT
                       p.postid,
                       p.userid,
                       p.dateposted,
                       p.textcontent,
                       u.picture,
                       p.reply_to_postid,
                       CASE WHEN l.liker IS NOT NULL THEN 1 ELSE 0 END AS is_liked,
                       CASE WHEN r.retweetuserid IS NOT NULL THEN 1 ELSE 0 END AS is_retweeted,
                       u.username
                   FROM PostInfo p
                   JOIN UserInfo u ON p.userid = u.userid
                   LEFT JOIN Likes l ON p.postid = l.originalpost AND l.liker = %s
                   LEFT JOIN Retweets r ON p.postid = r.originalpost AND r.retweetuserid = %s
                   LEFT JOIN Blocked b ON p.userid = b.blockee AND b.blocker = %s
                   WHERE p.reply_to_postid = %s AND b.blockee IS NULL
                   ORDER BY p.dateposted DESC;
               """
               rows = datatier.retrieve_all_rows(db_conn, sql_statement, [userid, userid, userid, postid])
               serialized_rows = serialize_rows(rows, include_likes_retweets=True)
           else:
               # Fetch general recent tweets (original logic)
               sql_statement = """
                   SELECT DISTINCT
                       p.postid,
                       p.userid,
                       p.dateposted,
                       p.textcontent,
                       u.picture,
                       p.reply_to_postid,
                       CASE WHEN l.liker IS NOT NULL THEN 1 ELSE 0 END AS is_liked,
                       CASE WHEN r.retweetuserid IS NOT NULL THEN 1 ELSE 0 END AS is_retweeted,
                       u.username
                   FROM PostInfo p
                   JOIN UserInfo u ON p.userid = u.userid
                   LEFT JOIN Followers f ON p.userid = f.followee
                   LEFT JOIN Likes l ON p.postid = l.originalpost AND l.liker = %s
                   LEFT JOIN Retweets r ON p.postid = r.originalpost AND r.retweetuserid = %s
                   LEFT JOIN Blocked b ON p.userid = b.blockee AND b.blocker = %s
                   WHERE (f.follower = %s OR p.userid = %s) AND p.reply_to_postid IS NULL AND b.blockee IS NULL
                   ORDER BY p.dateposted DESC
               """
               rows = datatier.retrieve_all_rows(db_conn, sql_statement, [userid, userid, userid, userid, userid])
               serialized_rows = serialize_rows(rows, include_likes_retweets=True)

           return {
               "statusCode": 200,
               "headers": CORS_HEADERS,
               "body": json.dumps(serialized_rows)
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