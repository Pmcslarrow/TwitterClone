# Post (Tweet)
# a. There should be a character limit on tweets

from configparser import ConfigParser
import os
from . import datatier
import json


def lambda_handler(event, context):
    """
    
    Post Tweet 
    --------------
    Receives:
        - The userid PK to identify the user to update
        - The key of textcontent and value associated to the tweet.
        - [OPTIONAL] The file key of the image(s) to be uploaded to S3.
    
    On Success:
        - Adds new tweet to PostInfo table

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
        
        if "textcontent" not in event_body:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "textcontent missing."
                })
            }
        
        userid = event_body['userid']
        textcontent = event_body['textcontent']
        image_file_key = event_body.get('image_file_key', None)

        if len(textcontent) > 500:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Text content exceeds 500 characters."
                })
            }
    
        print("Printing event object: ")
        print(event)
        print()


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
        # Making changes in database
        #
        try:
            sql_statement = """
                INSERT INTO PostInfo (userid, dateposted, textcontent, image_file_key)
                VALUES (%s, CURRENT_TIMESTAMP, %s, %s);
            """

            print("Printing SQL statement: ")
            print(sql_statement)
            print()
            print("Printing values to be inserted: ")
            print(f"userid: {userid}")
            print(f"textcontent: {textcontent}")
            print(f"image_file_key: {image_file_key}")

            datatier.perform_action(db_conn, sql_statement, [userid, textcontent, image_file_key])
           

            print("Update successful.")

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Post posted successfully."
                })
            }

        except Exception as e:
            print("Updating database ERR: ", e)

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"An error occurred (post_tweet): {str(e)}"
            })
        }