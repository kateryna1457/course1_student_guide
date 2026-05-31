CREATE TABLE IF NOT EXISTS s_university.t_groups (
    id SERIAL,
    name VARCHAR(20) NOT NULL UNIQUE,
    specialty_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    admission_year INTEGER NOT NULL,
    CONSTRAINT pk_groups PRIMARY KEY (id),
    CONSTRAINT fk_groups_specialty FOREIGN KEY (specialty_id)
        REFERENCES s_university.t_specialties(id) ON DELETE RESTRICT,
    CONSTRAINT fk_groups_course FOREIGN KEY (course_id)
        REFERENCES s_university.t_courses(id) ON DELETE RESTRICT,
    CONSTRAINT chk_groups_admission_year CHECK (admission_year BETWEEN 1900 AND 2100)
);

CREATE INDEX IF NOT EXISTS idx_groups_name ON s_university.t_groups(name);
CREATE INDEX IF NOT EXISTS idx_groups_specialty_id ON s_university.t_groups(specialty_id);
CREATE INDEX IF NOT EXISTS idx_groups_course_id ON s_university.t_groups(course_id);

DO $$
BEGIN
    RAISE NOTICE 'Table [s_university.t_groups] created successfully';
END $$;
