CREATE TABLE service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE task (
    id TEXT PRIMARY KEY NOT NULL,
    status TEXT NOT NULL DEFAULT 'available',
    service_id INTEGER NOT NULL REFERENCES service(id),
    generator_type TEXT NOT NULL,
    generator_options TEXT NOT NULL,
    timestamp INTEGER NULL DEFAULT NULL,
    ip_address TEXT NULL DEFAULT NULL,
    username TEXT NULL DEFAULT NULL,
    data_file TEXT NULL DEFAULT NULL
);

CREATE TABLE statistics (
    username TEXT NOT NULL,
    service_id INTEGER NOT NULL REFERENCES service(id),
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (username, service_id) ON CONFLICT IGNORE
);
