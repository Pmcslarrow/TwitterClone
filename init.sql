DROP DATABASE IF EXISTS TwitterClone;
CREATE DATABASE TwitterClone;
GRANT ALL PRIVILEGES ON TwitterClone.* TO 'test_user'@'%';
FLUSH PRIVILEGES;

USE TwitterClone;

-- Drop tables in reverse dependency order to avoid FK issues
DROP TABLE IF EXISTS Likes;
DROP TABLE IF EXISTS Retweets;
DROP TABLE IF EXISTS Blocked;
DROP TABLE IF EXISTS Followers;
DROP TABLE IF EXISTS PostInfo;
DROP TABLE IF EXISTS UserInfo;

-- Create tables
CREATE TABLE UserInfo (
    userid VARCHAR(320) PRIMARY KEY, -- userid is now going to be an EMAIL
    username VARCHAR(50) NOT NULL UNIQUE, -- squished thing mike and I discussed
    bio TEXT,
    picture TEXT
);

CREATE TABLE PostInfo (
    postid INT PRIMARY KEY AUTO_INCREMENT,
    userid VARCHAR(320),
    dateposted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    textcontent TEXT,
    image_file_key TEXT NULL,
    reply_to_postid INT NULL, -- FIXME: add tests in backend
    FOREIGN KEY (userid) REFERENCES UserInfo(userid) ON DELETE CASCADE,
    FOREIGN KEY (reply_to_postid) REFERENCES PostInfo(postid) ON DELETE CASCADE
);

ALTER TABLE PostInfo AUTO_INCREMENT = 20001;  -- starting value

CREATE TABLE Followers (
    follower VARCHAR(320),
    followee VARCHAR(320),
    PRIMARY KEY (follower, followee),
    FOREIGN KEY (follower) REFERENCES UserInfo(userid) ON DELETE CASCADE,
    FOREIGN KEY (followee) REFERENCES UserInfo(userid) ON DELETE CASCADE
);

CREATE TABLE Blocked (
    blocker VARCHAR(320),
    blockee VARCHAR(320),
    PRIMARY KEY (blocker, blockee),
    FOREIGN KEY (blocker) REFERENCES UserInfo(userid) ON DELETE CASCADE,
    FOREIGN KEY (blockee) REFERENCES UserInfo(userid) ON DELETE CASCADE
);

CREATE TABLE Retweets (
    retweetuserid VARCHAR(320),
    originalpost INT,
    PRIMARY KEY (retweetuserid, originalpost),
    FOREIGN KEY (retweetuserid) REFERENCES UserInfo(userid) ON DELETE CASCADE,
    FOREIGN KEY (originalpost) REFERENCES PostInfo(postid) ON DELETE CASCADE
);

CREATE TABLE Likes (
    liker VARCHAR(320),
    originalpost INT,
    PRIMARY KEY (liker, originalpost),
    FOREIGN KEY (liker) REFERENCES UserInfo(userid) ON DELETE CASCADE,
    FOREIGN KEY (originalpost) REFERENCES PostInfo(postid) ON DELETE CASCADE
);