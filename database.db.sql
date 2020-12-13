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
