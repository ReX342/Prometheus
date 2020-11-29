import os
from sqlite3.dbapi2 import Timestamp
import discord
import sqlite3
from datetime import datetime 
import os
from dotenv import load_dotenv

if os.path.isfile('.env'):
    load_dotenv('.env')

TOKEN = os.environ.get('TOKEN') 
if TOKEN == None:
    raise Exception('No Discord developper application TOKEN is set')


db_schema_script = '''BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "attachments" (
	"attachment_id"	INTEGER,
	"attachment_filename"	TEXT,
	"attachment_url"	TEXT,
	"attachment_message_id"	INTEGER,
	PRIMARY KEY("attachment_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "messages" (
	"message_id"	INTEGER,
	"message_content"	TEXT,
	"message_author"	TEXT,
	"message_channel"	TEXT,
	"Timestamp"	TEXT NOT NULL,
	PRIMARY KEY("message_id" AUTOINCREMENT)
);
COMMIT;'''

#Making dbase in case it doesn't exist
with sqlite3.connect('trashfire.db') as conn:
    cursor = conn.cursor()
    cursor.executescript(db_schema_script)
    conn.commit()
    print("Executed DB schema script")
    cursor.close()

client = discord.Client()
# Not Null Timestamp
utc_time = datetime.utcnow().isoformat()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Documentation: https://discordpy.readthedocs.io/en/latest/api.html#discord.TextChannel 
    print("type", message.channel.type) # 'text' or 'private'
    
    if  str(message.channel.type) == 'text' and \
        message.channel.name == "stream-of-consciousness":
        with sqlite3.connect("trashfire.db") as conn:
            utc_time = datetime.utcnow().isoformat()
            cursor = conn.execute("INSERT INTO messages "
                "(message_content, message_author, message_channel, Timestamp) "
                "VALUES (?, ?, ?, ?) ", (message.content, 
                f"{message.author.name}#{message.author.discriminator}" , 
                message.channel.name, utc_time))
            message_id = cursor.lastrowid
            conn.commit()
             
            for attachment in message.attachments:
                cursor.execute("INSERT INTO attachments "
                    "(attachment_filename, attachment_url, attachment_message_id) "
                    "VALUES (?, ?, ?) ", (attachment.filename, attachment.url, 
                    message_id))
                conn.commit()
            cursor.close()

client.run(TOKEN)