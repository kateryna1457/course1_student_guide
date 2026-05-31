CREATE SCHEMA IF NOT EXISTS s_university;
SET search_path TO s_university, public;
GRANT ALL ON SCHEMA s_university TO student_user;

DO $$
BEGIN
    RAISE NOTICE 'Schema [s_university] created successfully';
END $$;
