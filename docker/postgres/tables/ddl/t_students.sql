-- ==========================================
-- Table: s_university.t_students
-- Description: Student records
-- ==========================================

CREATE TABLE IF NOT EXISTS s_university.t_students (
    id SERIAL,
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    patronymic VARCHAR(100),
    student_id_number VARCHAR(20) NOT NULL UNIQUE,
    group_id INTEGER NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    birth_date DATE NOT NULL,
    enrollment_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT pk_students PRIMARY KEY (id),
    CONSTRAINT fk_students_group FOREIGN KEY (group_id)
        REFERENCES s_university.t_groups(id) ON DELETE RESTRICT,
    CONSTRAINT chk_students_email CHECK (
        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    ),
    CONSTRAINT chk_students_birth_date CHECK (
        birth_date BETWEEN '1900-01-01' AND CURRENT_DATE - INTERVAL '15 years'
    )
);

-- Create indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_students_last_name ON s_university.t_students(last_name);
CREATE INDEX IF NOT EXISTS idx_students_email ON s_university.t_students(email);
CREATE INDEX IF NOT EXISTS idx_students_student_id_number ON s_university.t_students(student_id_number);
CREATE INDEX IF NOT EXISTS idx_students_group_id ON s_university.t_students(group_id);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Table [s_university.t_students] created successfully';
END $$;
