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
