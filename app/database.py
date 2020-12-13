import sqlite3
import bcrypt
from uuid import uuid4
from app import app
from flask import url_for
from datetime import datetime, timedelta

DATABASE = app.config['DATABASE']

def hash_password(password):
    """Hashes an utf-8 string and returns an utf-8 string of the hash"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def create_user(email, password):
    """Creates a new user"""
    with sqlite3.connect(DATABASE) as conn:
        pw_hash = hash_password(password)
        conn.execute("INSERT INTO users (user_email, user_hash) VALUES (?, ?)", (email, pw_hash))
        conn.commit()

def check_password(email, password):
    """Return True upon success, False upon failure"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_hash FROM users WHERE user_email = ?;", (email,))
        user_hash = cursor.fetchone()
        if user_hash == None:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user_hash[0].encode('utf-8'))

def get_user_id(email):
    """Return the user_id for a given email"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_email = ?;", (email,))
        user_id = cursor.fetchone()[0]
        return user_id

def is_valid_user_id(user_id):
    """Returns True if the user_id exists, False if not"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id FROM users WHERE user_id = ?;", (user_id,))    
        return cursor.fetchone()[0] != None

def get_user(user_id):
    """Return a user based on a user_id"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT user_id, user_email, "
            "user_nickname, user_verified_email "
            "FROM users "
            "WHERE user_id = ?;", (user_id,))
        row = cursor.fetchone()
        user_id, user_email, user_nickname, user_verified_email = row
        user = {
            "user_id":user_id,
            "user_email": user_email,
            "user_nickname": user_nickname,
            "user_verified_email": user_verified_email
        }
        return user

def save_nickname(user_id, user_nickname):
    """Save the user nickname"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("UPDATE users SET user_nickname = ? "
            "WHERE user_id = ?", (user_nickname, user_id))
        conn.commit()

def generate_verification_link(user_id):
    code = str(uuid4())
    dt_today = datetime.now()
    dt_delta = timedelta(days=2)
    dt_future = dt_today + dt_delta
    str_future = dt_future.isoformat()

    with sqlite3.connect(DATABASE) as conn:
        conn.execute("INSERT INTO activations "
            "(act_code, act_user_id, act_expiration) "
            "VALUES (?, ?, ?)", (code, user_id, str_future))
        conn.commit()
    
    return url_for('activate_email', activation_code=code, _external=True)

def verify_user_email(activation_code):
    """Return True on success, False on failure"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT act_user_id, act_expiration FROM activations WHERE act_code = ?", (activation_code,))
        user_id, act_expiration = cursor.fetchone()
        if user_id == None:
            return False
        # TODO check expiration date
        cursor.execute("UPDATE users SET user_verified_email = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        print("USER email is verified!")
        return True
    
def nickname_exists(user_nickname):
    """Return True if nickname already exists, False if allowed"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute("SELECT "
            "user_nickname "
            "FROM users "
            "WHERE user_nickname = ?;", (user_nickname,))
        row = cursor.fetchone()
        user_nickname = row
        if row == None:
            return False
        else:
            return True
        
        

# Create the database tables in case that they do not exist yet.
db_schema_script = """
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "activations" (
	"act_id"	INTEGER,
	"act_code"	TEXT NOT NULL,
	"act_user_id"	INTEGER NOT NULL,
	"act_expiration"	TEXT NOT NULL,
	PRIMARY KEY("act_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "users" (
	"user_id"	INTEGER,
	"user_email"	TEXT UNIQUE,
	"user_hash"	TEXT,
	"user_nickname"	TEXT UNIQUE,
	"user_verified_email"	INTEGER DEFAULT 0,
	PRIMARY KEY("user_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "ratings" (
	"ratings_id"	INTEGER,
	"ratings_usr_id"	INTEGER,
	"ratings_attachment_id"	INTEGER,
	"ratings_rating"	INTEGER,
	PRIMARY KEY("ratings_id" AUTOINCREMENT)
);
COMMIT;
"""
with sqlite3.connect(DATABASE) as conn:
    cursor = conn.cursor()
    cursor.executescript(db_schema_script)
    conn.commit()
    print("Executed DB schema script")
    cursor.close()

def get_content():
    with sqlite3.connect('discordbot/trashfire.db') as conn:
        cursor = conn.execute("SELECT "
            "message_content, Timestamp "
            "FROM messages "
        )
        #print(cursor.fetchall())
        #messages_list = []
        return cursor.fetchall()
        #cursor.close()

def get_attachment():
    with sqlite3.connect('discordbot/trashfire.db') as conn:
        cursor = conn.execute("""SELECT attachment_url, 
                              attachment_filename, 
                              message_author, 
                              Timestamp, 
                              message_content 
                              FROM attachments, messages 
                              WHERE message_id = attachment_message_id 
                              ORDER by Timestamp desc LIMIT 50,50;"""
        )
        #print(cursor.fetchall())
        #messages_list = []
        return cursor.fetchall()
        #cursor.close()
        
class Post():
    def __init__(self, attachment_id, attachment_filename, attachment_url, 
        attachment_message_id, message_content, message_author, 
        message_channel, timestamp):
        self.attachment_id = attachment_id
        self.message_id = attachment_message_id
        self.filename = attachment_filename
        self.url = attachment_url
        if attachment_url.endswith('.png'):
            self.type = 'img'
        else:
            self.type = 'other'
        self.content = message_content
        self.author = message_author
        self.nickname = message_author.split('#')[0]
        self.channel = message_channel
        self.timestamp = timestamp

    def toDict(self):
            """Create a dict of the Post object so it can be converted to JSON"""
            return {
                "nickname": self.nickname,
                "timestamp": self.timestamp,
                "content": self.content,
                "type": self.type,
                "url": self.url,
                "filename": self.filename
            }

#region database stuff
TRASHFIRE = app.config['TRASHFIRE']
def get_posts_offset_based(offset=0, amount=5):
    with sqlite3.connect(TRASHFIRE) as conn:
        cursor = conn.execute("""
            SELECT attachment_id, attachment_filename, attachment_url, 
                attachment_message_id, message_content, message_author, 
                message_channel, Timestamp
            FROM attachments
            JOIN messages ON attachment_message_id = message_id
            ORDER BY datetime(Timestamp) DESC
            LIMIT ?,?;
        """, (offset, amount))
        rows = cursor.fetchall()
        posts = []
        for row in rows:
            post = Post(*row)
            posts.append(post)
        return posts
    
def get_random(number_posts=5):
    with sqlite3.connect(TRASHFIRE) as conn:
        cursor = conn.execute("""
            SELECT attachment_id, attachment_filename, attachment_url, 
                attachment_message_id, message_content, message_author, 
                message_channel, Timestamp
            FROM attachments
            JOIN messages ON attachment_message_id = message_id
            WHERE attachment_id
            IN (SELECT attachment_id FROM attachments ORDER BY RANDOM() LIMIT ?)
            ORDER BY datetime(Timestamp) DESC;
        """, (number_posts,))
        rows = cursor.fetchall()
        posts = []
        for row in rows:
            post = Post(*row)
            posts.append(post)
        return posts

def get_posts_cursor_based(cursor, amount=5):
    with sqlite3.connect(app.config['TRASHFIRE']) as conn:
        cursor = conn.execute("""
            SELECT attachment_id, attachment_filename, attachment_url, 
                attachment_message_id, message_content, message_author, 
                message_channel, Timestamp
            FROM attachments
            JOIN messages ON attachment_message_id = message_id
            WHERE datetime(?) > datetime(Timestamp)
            ORDER BY datetime(Timestamp) DESC
            LIMIT ?;
        """, (cursor, amount))
        rows = cursor.fetchall()
        posts = []
        timestamp_last_post = cursor # init with cursor
        for row in rows:
            post = Post(*row)
            posts.append(post)
            timestamp_last_post = post.timestamp
        
        return posts, timestamp_last_post

def get_random_tweet():
    with sqlite3.connect(TRASHFIRE) as conn:
        cursor = conn.execute("""
            SELECT message_content, Timestamp
            FROM messages 
            ORDER BY RANDOM();
        """, 
        )
        return cursor.fetchall()

# https://mdbootstrap.com/plugins/jquery/rating/ and pipe to database to save rating
# Make sure the page doesn't refresh on click/voting

# Have a messages.send discordbot send oldest message up to and including ragna's meme
