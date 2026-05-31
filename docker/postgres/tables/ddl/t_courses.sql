-- ==========================================
-- Table: s_university.t_courses
-- Description: Academic course years (1-6)
-- ==========================================

CREATE TABLE IF NOT EXISTS s_university.t_courses (
    id SERIAL,
    course_number INTEGER NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    CONSTRAINT pk_courses PRIMARY KEY (id),
    CONSTRAINT chk_courses_number CHECK (course_number BETWEEN 1 AND 6)
);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Table [s_university.t_courses] created successfully';
END $$;
