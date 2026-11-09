CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('inbound', 'outbound')),
    body TEXT NOT NULL,
    whatsapp_message_id TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_phone ON messages(phone);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
