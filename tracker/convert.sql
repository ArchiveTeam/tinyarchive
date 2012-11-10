ALTER TABLE task ADD COLUMN timestamp INTEGER NULL DEFAULT NULL;
UPDATE task SET timestamp = assigned_when;

ALTER TABLE task ADD COLUMN ip_address TEXT NULL DEFAULT NULL;
UPDATE task SET ip_address = assigned_to;
