import pytest
import pymysql
import json
from lambda_functions.update_profile import lambda_handler

@pytest.fixture(scope="module")
def db_connection():
    # Connect to the local MySQL database running in Docker
    connection = pymysql.connect(
        host="127.0.0.1",
        user="test_user",
        password="test_pass",
        database="TwitterClone",
        port=3306
    )
    yield connection
    connection.close()

@pytest.fixture
def setup_test_data(db_connection):
    # Insert test data into the database
    with db_connection.cursor() as cursor:
        cursor.execute("DELETE FROM UserInfo;")  # Clear existing data
        cursor.execute("""
            INSERT INTO UserInfo (userid, username, bio, picture)
            VALUES ('123', 'test_user', 'Test bio', 'test_picture_url');
        """)
        db_connection.commit()

def test_successful_update(db_connection, setup_test_data):
    # Define the event to simulate the Lambda invocation
    event = {
        "body": json.dumps({
            "userid": "123",
            "bio": "Updated bio",
            "username": "updated_user",
            "picture": "updated_picture_url"
        })
    }
    context = {}

    # Invoke the Lambda function
    response = lambda_handler(event, context)

    # Assert the response
    assert response["statusCode"] == 200
    assert "Profile updated successfully" in response["body"]

    # Verify the database was updated
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT bio, username, picture FROM UserInfo WHERE userid = '123';")
        result = cursor.fetchone()
        assert result == ("Updated bio", "updated_user", "updated_picture_url")

def test_successful_update_single_key(db_connection, setup_test_data):
    # Passes in key value pairs, but is missing username and picture updates.
    event = {
        "body": json.dumps({
            "userid": "123",
            "bio": "Updated bio"
        })
    }
    context = {}

    # Invoke the Lambda function
    response = lambda_handler(event, context)

    # Assert the response
    assert response["statusCode"] == 200
    assert "Profile updated successfully" in response["body"]

    # Verify the database was updated
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT bio FROM UserInfo WHERE userid = '123';")
        result = cursor.fetchone()
        assert result[0] == "Updated bio"

def test_failure_missing_userid(db_connection):
    # Define the event with missing userid
    event = {
        "body": {
            # "userid": "123",  # Missing userid
            "bio": "Updated bio",
            "username": "updated_user"
        }
    }
    context = {}

    # Invoke the Lambda function
    response = lambda_handler(event, context)

    # Assert the response
    assert response["statusCode"] == 400
    assert "userid missing" in response["body"]