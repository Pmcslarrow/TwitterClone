import pytest
import json
from lambda_functions.delete_post import lambda_handler
import pymysql

@pytest.fixture(scope="module")
def db_connection():
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
    with db_connection.cursor() as cursor:
        cursor.execute("DELETE FROM UserInfo;")
        cursor.execute("""
            INSERT INTO UserInfo (userid, username, bio, picture)
            VALUES ('123', 'test_user', 'Test bio', 'test_picture_url');
        """)
        db_connection.commit()

        
    with db_connection.cursor() as cursor:
        cursor.execute("DELETE FROM PostInfo;")
        cursor.execute("""
            INSERT INTO PostInfo (postid, userid, textcontent)
            VALUES ('1', '123', 'This is a test post.');
        """)
        db_connection.commit()

    yield  
    # Cleanup after tests

    with db_connection.cursor() as cursor:
        cursor.execute("DELETE FROM UserInfo;")
        cursor.execute("DELETE FROM PostInfo;")
        db_connection.commit()

@pytest.fixture
def valid_delete_event():
    return {
        "body": json.dumps({
            "postid": "1"
        })
    }

@pytest.fixture
def missing_postid_event():
    return {
        "body": json.dumps({})
    }

@pytest.fixture
def non_existent_postid_event():
    return {
        "body": json.dumps({
            "postid": "999"
        })
    }

def test_successful_post_deletion(valid_delete_event, setup_test_data):
    context = {}
    response = lambda_handler(valid_delete_event, context)
    
    # Ensure the response is successful
    assert response["statusCode"] == 200
    assert "Post posted successfully." in response["body"]

def test_missing_postid(missing_postid_event, setup_test_data):
    context = {}
    response = lambda_handler(missing_postid_event, context)

    assert response["statusCode"] == 400
    assert "postid missing." in response["body"]

def test_non_existent_postid(non_existent_postid_event, setup_test_data):
    context = {}
    response = lambda_handler(non_existent_postid_event, context)

    # Ensure the response handles non-existent postid gracefully
    assert response["statusCode"] == 200
    assert "Post posted successfully." in response["body"]