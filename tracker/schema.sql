CREATE TABLE service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE task (
    id TEXT PRIMARY KEY NOT NULL,
    status TEXT NOT NULL DEFAULT 'free',
    service_id INTEGER NOT NULL REFERENCES service(id),
    generator_type TEXT NOT NULL,
    generator_options TEXT NOT NULL,
    timestamp INTEGER NULL DEFAULT NULL,
    ip_address TEXT NULL DEFAULT NULL,
    finished_by TEXT NULL DEFAULT NULL,
    data_file TEXT NULL DEFAULT NULL
);
