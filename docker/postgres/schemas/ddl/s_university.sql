-- ==========================================
-- Create University Schema
-- ==========================================

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS s_university;

-- Set search path to include university schema
SET search_path TO s_university, public;

-- Grant privileges to the database user
GRANT ALL ON SCHEMA s_university TO student_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Schema [s_university] created successfully';
END $$;
