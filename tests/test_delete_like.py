import pytest
import json
from lambda_functions.delete_like import lambda_handler
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
        # Clear existing data in reverse dependency order
        cursor.execute("DELETE FROM Likes;")
        cursor.execute("DELETE FROM PostInfo;")
        cursor.execute("DELETE FROM UserInfo;")
        
        # Insert test users
        cursor.execute("""
            INSERT INTO UserInfo (userid, username, bio, picture)
            VALUES 
                ('user1', 'User One', 'Bio 1', 'pic1'),
                ('user2', 'User Two', 'Bio 2', 'pic2');
        """)
        
        # Insert test posts
        cursor.execute("""
            INSERT INTO PostInfo (postid, userid, textcontent)
            VALUES 
                (20001, 'user1', 'Post by User One'),
                (20002, 'user2', 'Post by User Two');
        """)

        # Insert test likes
        cursor.execute("""
            INSERT INTO Likes (liker, originalpost)
            VALUES 
                ('user1', 20001),
                ('user2', 20002);
        """)
        
        db_connection.commit()
        print("Database changes committed.")
    print("Test data setup complete.")

@pytest.fixture
def valid_delete_event():
    return {
        "body": json.dumps({
            "userid": "user1",
            "postid": 20001
        })
    }

@pytest.fixture
def missing_userid_event():
    return {
        "body": json.dumps({
            "postid": 20001
        })
    }

@pytest.fixture
def missing_postid_event():
    return {
        "body": json.dumps({
            "userid": "user1"
        })
    }

def test_successful_delete(valid_delete_event, setup_test_data, db_connection):
    context = {}
    response = lambda_handler(valid_delete_event, context)
    
    # Ensure the response is successful
    assert response["statusCode"] == 200
    assert "Successfully removed like" in response["body"]

    # Verify the like was removed from the database
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Likes WHERE liker = 'user1' AND originalpost = 20001;")
        assert cursor.fetchone() is None

def test_missing_userid(missing_userid_event, setup_test_data):
    context = {}
    response = lambda_handler(missing_userid_event, context)

    # Ensure the response returns an error for missing userid
    assert response["statusCode"] == 400
    assert "userid missing." in response["body"]

def test_missing_postid(missing_postid_event, setup_test_data):
    context = {}
    response = lambda_handler(missing_postid_event, context)

    # Ensure the response returns an error for missing postid
    assert response["statusCode"] == 400
    assert "postid missing." in response["body"]