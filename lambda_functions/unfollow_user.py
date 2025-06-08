## unfollow_user.py

from configparser import ConfigParser
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


def lambda_handler(event, context):
    """
    unfollow_user.py
    --------------
    Receives:
        - The follower userid (who is unfollowing)
        - The followee username (who is being unfollowed)
    
    On Success:
        - Removes a follower relationship from the Followers table
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

        if "follower" not in event_body:
            return {
                "statusCode": 400,
                            "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "follower userid missing."
                })
            }
        
        if "followee_username" not in event_body:
            return {
                "statusCode": 400,
                            "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "followee_username missing."
                })
            }
        
        follower = event_body['follower']
        followee_username = event_body['followee_username']

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
            # Get followee userid from username
            check_followee_sql = "SELECT userid FROM UserInfo WHERE username = %s;"
            followee_result = datatier.retrieve_all_rows(db_conn, check_followee_sql, [followee_username])
            
            if not followee_result:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Followee user does not exist."
                    })
                }
            
            followee = followee_result[0][0]  # Extract userid from result
            
            # Check if the relationship exists
            check_relationship_sql = "SELECT * FROM Followers WHERE follower = %s AND followee = %s;"
            existing_relationship = datatier.retrieve_all_rows(db_conn, check_relationship_sql, [follower, followee])
            
            if not existing_relationship:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Cannot unfollow: relationship does not exist."
                    })
                }

            # Remove follower relationship
            sql_statement = """
                DELETE FROM Followers
                WHERE follower = %s AND followee = %s;
            """

            datatier.perform_action(db_conn, sql_statement, [follower, followee])

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "Successfully unfollowed user."
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
                "message": f"An error occurred (unfollow_user): {str(e)}"
            })
        }
