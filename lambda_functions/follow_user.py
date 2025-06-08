## follow_user.py

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
    follow_user.py
    --------------
    Receives:
        - The follower userid (who is following)
        - The followee username (who is being followed)
    
    On Success:
        - Adds a follower relationship to the Followers table
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
            # Check if follower exists
            check_follower_sql = "SELECT userid FROM UserInfo WHERE userid = %s;"
            follower_result = datatier.retrieve_all_rows(db_conn, check_follower_sql, [follower])
            
            if not follower_result:
                return {
                    "statusCode": 404,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Follower user does not exist."
                    })
                }
                
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
            
            # Check if users are trying to follow themselves
            if follower == followee:
                return {
                    "statusCode": 400,
                                "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Users cannot follow themselves."
                    })
                }
                
            # Check if the relationship already exists
            check_relationship_sql = "SELECT * FROM Followers WHERE follower = %s AND followee = %s;"
            existing_relationship = datatier.retrieve_all_rows(db_conn, check_relationship_sql, [follower, followee])
            
            if existing_relationship:
                return {
                    "statusCode": 400,
                                "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "User is already following this account."
                    })
                }
                
            # Check if the user is blocked
            check_blocked_sql = "SELECT * FROM Blocked WHERE blocker = %s AND blockee = %s;"
            is_blocked = datatier.retrieve_all_rows(db_conn, check_blocked_sql, [followee, follower])
            
            if is_blocked:
                return {
                    "statusCode": 403,
                    "headers": CORS_HEADERS,
                                "body": json.dumps({
                        "message": "Cannot follow user: you have been blocked."
                    })
                }

            # Add follower relationship
            sql_statement = """
                INSERT INTO Followers (follower, followee)
                VALUES (%s, %s);
            """

            datatier.perform_action(db_conn, sql_statement, [follower, followee])

            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                                "body": json.dumps({
                    "message": "Successfully followed user."
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
                "message": f"An error occurred (follow_user): {str(e)}"
            })
        }
