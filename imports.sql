CREATE TABLE service (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE import (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imported INTEGER NOT NULL,
    status TEXT NOT NULL,
    service_id INTEGER NOT NULL REFERENCES service(id),
    filename TEXT NOT NULL,
    generator_type TEXT NULL DEFAULT NULL,
    generator_options TEXT NULL DEFAULT NULL
);
