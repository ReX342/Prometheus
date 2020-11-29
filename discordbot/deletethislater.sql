BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "messages" (
    "message_id"    INTEGER,
    "message_content"    TEXT,
    "message_author"    TEXT,
    "message_channel"    TEXT,
    PRIMARY KEY("message_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "attachments" (
    "attachment_id"    INTEGER,
    "attachment_filename"    TEXT,
    "attachment_url"    TEXT,
    "attachment_message_id"    INTEGER,
    PRIMARY KEY("attachment_id" AUTOINCREMENT)
);
COMMIT;