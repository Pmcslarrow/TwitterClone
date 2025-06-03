import pytest
import json
from lambda_functions.post_tweet import lambda_handler
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
        cursor.execute("DELETE FROM PostInfo;")
        cursor.execute("""
            INSERT INTO UserInfo (userid, username, bio, picture)
            VALUES ('123', 'test_user', 'Test bio', 'test_picture_url');
        """)
        db_connection.commit()

@pytest.fixture
def valid_event():
    return {
        "body": json.dumps({
            "userid": "123",
            "textcontent": "This is a valid tweet."
        })
    }

@pytest.fixture
def valid_event_with_image():
    return {
        "body": json.dumps({
            "userid": "123",
            "textcontent": "This is a valid tweet with an image.",
            "image_file_key": "uploads/123/image1.jpg"
        })
    }

@pytest.fixture
def long_tweet_event():
    return {
        "body": json.dumps({
            "userid": "123",
            "textcontent": "A" * 501  # 501 characters long
        })
    }

@pytest.fixture
def missing_userid_event():
    return {
        "body": json.dumps({
            "textcontent": "This tweet has no userid."
        })
    }

def test_successful_tweet_posting(valid_event, setup_test_data, db_connection):
    context = {}
    response = lambda_handler(valid_event, context)
    
    # Ensure the response is successful
    assert response["statusCode"] == 200
    assert "Post posted successfully." in response["body"]

    # Verify the database entry
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PostInfo WHERE userid = '123';")
        result = cursor.fetchone()
        assert result is not None
        assert result[3] == "This is a valid tweet."  # textcontent
        assert result[4] is None  # image_file_key should be NULL

def test_successful_tweet_posting_with_image(valid_event_with_image, setup_test_data, db_connection):
    context = {}
    response = lambda_handler(valid_event_with_image, context)
    
    # Ensure the response is successful
    assert response["statusCode"] == 200
    assert "Post posted successfully." in response["body"]

    # Verify the database entry
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM PostInfo WHERE userid = '123';")
        result = cursor.fetchone()
        assert result is not None
        assert result[3] == "This is a valid tweet with an image."  # textcontent
        assert result[4] == "uploads/123/image1.jpg"  # image_file_key

def test_tweet_exceeding_character_limit(long_tweet_event, setup_test_data):
    context = {}
    response = lambda_handler(long_tweet_event, context)

    assert response["statusCode"] == 400
    assert "Text content exceeds 500 characters." in response["body"]

def test_missing_userid(missing_userid_event, setup_test_data):
    context = {}
    response = lambda_handler(missing_userid_event, context)

    assert response["statusCode"] == 400
    assert "userid missing." in response["body"]