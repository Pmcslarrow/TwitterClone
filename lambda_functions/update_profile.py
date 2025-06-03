from configparser import ConfigParser
import os
import datatier
import json
import boto3

def lambda_handler(event, context):
    """
    
    Update profile
    --------------
    Receives:
        - The userid PK to identify the user to update
        - The key(s) of what the user wants changed: bio, username, picture. 
        - The value(s) of what the user wants to change the key to

    On Success:
        - Updates database representation of key to new value.

    """
    try:
        if "body" not in event:
            raise Exception("User error. No data received.")
        
        if "userid" not in event['body']:
            raise Exception("userid missing.")
        
        event = json.loads(event['body'])
        userid = event['userid']
    
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
        # Extracting user changes
        #
        #
        # updates = { bio: new_bio, username: new_username, picture: new_picture } 
        # Allows us to iterate through things to actually update. 
        #

        print("*** Extracting user input ***")

        updates = {} 

        if "bio" in event:
            updates['bio'] = event['bio']

        if "username" in event:
            updates['username'] = event['username']

        if "picture" in event:
            updates['picture'] = event["picture"]


        #
        # Making changes 
        #

        try:
            sql_set_statements = ", ".join([f"{key} = %s" for key in updates.keys()])

            print("sql_set_statement: ")
            print(sql_set_statements)

            update_sql_statement = f"""
                UPDATE UserInfo
                SET {sql_set_statements}
                WHERE userid = %s;
            """

            print("update_sql_statement: ")
            print(update_sql_statement)

            datatier.perform_action(db_conn, update_sql_statement, list(updates.values()) + [userid])

            print("Update successful.")

            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": "Profile updated successfully."
                })
            }

        except Exception as e:
            print("Updating database ERR: ", e)

    except Exception as e:
        print("ERR: ", e)
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": f"An error occurred (update_profile): {str(e)}"
            })
        }