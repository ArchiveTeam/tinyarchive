ALTER TABLE task ADD COLUMN timestamp INTEGER NULL DEFAULT NULL;
UPDATE task SET timestamp = assigned_when;
