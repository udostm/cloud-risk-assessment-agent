CREATE TABLE IF NOT EXISTS logins (
    "id" UUID PRIMARY KEY,
    "createdAt" TEXT,
    "passwordHash" TEXT
);


INSERT INTO logins ("id", "passwordHash", "createdAt")
VALUES ('0f002ab0-d160-431f-80f7-3b434089ba82', '\$2b\$12$Fd7fzbmDiEekqjl4dGvH6e8fx106uHkGxPgC.cxeqXWdHQoUZ.cu6', '2025-02-10T21:14:25.875315+00');


CREATE TABLE  IF NOT EXISTS users (
    "id" UUID PRIMARY KEY,
    "identifier" TEXT NOT NULL UNIQUE,
    "metadata" JSONB NOT NULL,
    "createdAt" TEXT
);

INSERT INTO users ("id", "identifier", "metadata", "createdAt")
VALUES ('0f002ab0-d160-431f-80f7-3b434089ba82', 'admin', '{"role": "admin"}', '2025-02-10T21:14:25.875315+00');

CREATE TABLE IF NOT EXISTS threads (
    "id" UUID PRIMARY KEY,
    "createdAt" TEXT,
    "name" TEXT,
    "userId" UUID,
    "userIdentifier" TEXT,
    "tags" TEXT[],
    "metadata" JSONB,
    FOREIGN KEY ("userId") REFERENCES users("id") ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS steps (
    "id" UUID PRIMARY KEY,
    "name" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "threadId" UUID NOT NULL,
    "parentId" UUID,
    "streaming" BOOLEAN NOT NULL,
    "waitForAnswer" BOOLEAN,
    "isError" BOOLEAN,
    "metadata" JSONB,
    "tags" TEXT[],
    "input" TEXT,
    "output" TEXT,
    "createdAt" TEXT,
    "start" TEXT,
    "end" TEXT,
    "generation" JSONB,
    "showInput" TEXT,
    "language" TEXT,
    "indent" INT
);

CREATE TABLE IF NOT EXISTS elements (
    "id" UUID PRIMARY KEY,
    "threadId" UUID,
    "type" TEXT,
    "url" TEXT,
    "chainlitKey" TEXT,
    "name" TEXT NOT NULL,
    "display" TEXT,
    "objectKey" TEXT,
    "size" TEXT,
    "page" INT,
    "language" TEXT,
    "forId" UUID,
    "mime" TEXT
);

CREATE TABLE IF NOT EXISTS feedbacks (
    "id" UUID PRIMARY KEY,
    "forId" UUID NOT NULL,
    "threadId" UUID NOT NULL,
    "value" INT NOT NULL,
    "comment" TEXT
);

CREATE TABLE IF NOT EXISTS blob_storage (
    object_key VARCHAR PRIMARY KEY,
    data BYTEA,
    mime_type VARCHAR
);

