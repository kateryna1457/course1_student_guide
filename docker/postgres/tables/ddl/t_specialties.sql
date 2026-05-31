-- ==========================================
-- Table: s_university.t_specialties
-- Description: Academic specialties/programs
-- ==========================================

CREATE TABLE IF NOT EXISTS s_university.t_specialties (
    id SERIAL,
    name VARCHAR(200) NOT NULL UNIQUE,
    code VARCHAR(10) UNIQUE,
    description TEXT,
    CONSTRAINT pk_specialties PRIMARY KEY (id),
    CONSTRAINT chk_specialties_code CHECK (code IS NULL OR length(code) >= 2)
);

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Table [s_university.t_specialties] created successfully';
END $$;
