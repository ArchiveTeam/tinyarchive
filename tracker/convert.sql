ALTER TABLE task ADD COLUMN timestamp INTEGER NULL DEFAULT NULL;
UPDATE task SET timestamp = assigned_when;
UPDATE task SET assigned_when = NULL;

ALTER TABLE task ADD COLUMN ip_address TEXT NULL DEFAULT NULL;
UPDATE task SET ip_address = assigned_to;
UPDATE task SET ASSIGNED_TO = NULL;

ALTER TABLE task ADD COLUMN username TEXT NULL DEFAULT NULL;
UPDATE task SET username = finished_by;
UPDATE task SET finished_by = NULL;

UPDATE task SET status = 'available' WHERE status = 'free';
UPDATE task SET status = 'finished' WHERE status = 'done';

CREATE TABLE statistics (
    username TEXT NOT NULL,
    service_id INTEGER NOT NULL REFERENCES service(id),
    count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (username, service_id) ON CONFLICT IGNORE
);

ALTER TABLE service ADD COLUMN finished_tasks_count INTEGER NOT NULL DEFAULT 0;
