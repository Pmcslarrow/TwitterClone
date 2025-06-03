import pytest
import json
from lambda_functions.get_recent_tweets import lambda_handler
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
        cursor.execute("DELETE FROM Retweets;")
        cursor.execute("DELETE FROM Blocked;")
        cursor.execute("DELETE FROM Followers;")
        cursor.execute("DELETE FROM PostInfo;")
        cursor.execute("DELETE FROM UserInfo;")
        
        # Insert test users
        cursor.execute("""
            INSERT INTO UserInfo (userid, username, bio, picture)
            VALUES 
                ('user1', 'User One', 'Bio 1', 'pic1'),
                ('user2', 'User Two', 'Bio 2', 'pic2'),
                ('user3', 'User Three', 'Bio 3', 'pic3');
        """)
        
        # Insert test posts (postid will auto-increment)
        cursor.execute("""
            INSERT INTO PostInfo (userid, textcontent)
            VALUES 
                ('user1', 'Post by User One'),
                ('user2', 'Post by User Two'),
                ('user3', 'Post by User Three'),
                ('user1', 'Another post by User One');
        """)
        
        # Insert test followers
        cursor.execute("""
            INSERT INTO Followers (follower, followee)
            VALUES 
                ('user1', 'user2'),
                ('user1', 'user3');
        """)
        
        db_connection.commit()

@pytest.fixture
def valid_event():
    return {
        "body": json.dumps({
            "userid": "user1",
            "page": 1
        })
    }

@pytest.fixture
def missing_userid_event():
    return {
        "body": json.dumps({
            "page": 1
        })
    }

@pytest.fixture
def invalid_page_event():
    return {
        "body": json.dumps({
            "userid": "user1",
            "page": -1
        })
    }

def test_successful_retrieval(valid_event, setup_test_data):
    context = {}
    response = lambda_handler(valid_event, context)
    
    # Ensure the response is successful
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert isinstance(body, list) 
    assert len(body) == 4


def test_missing_userid(missing_userid_event, setup_test_data):
    context = {}
    response = lambda_handler(missing_userid_event, context)

    assert response["statusCode"] == 400
    assert "userid missing." in response["body"]

def test_invalid_page(invalid_page_event, setup_test_data):
    context = {}
    response = lambda_handler(invalid_page_event, context)

    assert response["statusCode"] == 400
    assert "Page number must" in json.loads(response["body"])['message']
