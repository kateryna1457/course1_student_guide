-- ==========================================
-- View: s_university.v_student_full_info
-- Description: Complete student information with joins
-- ==========================================

CREATE OR REPLACE VIEW s_university.v_student_full_info AS
SELECT
    s.id,
    s.last_name,
    s.first_name,
    s.patronymic,
    s.student_id_number,
    s.email,
    s.phone,
    s.birth_date,
    s.enrollment_date,
    g.id AS group_id,
    g.name AS group_name,
    g.admission_year,
    c.id AS course_id,
    c.course_number,
    c.name AS course_name,
    sp.id AS specialty_id,
    sp.name AS specialty_name,
    sp.code AS specialty_code,
    sp.description AS specialty_description
FROM s_university.t_students s
JOIN s_university.t_groups g ON s.group_id = g.id
JOIN s_university.t_courses c ON g.course_id = c.id
JOIN s_university.t_specialties sp ON g.specialty_id = sp.id;

-- Add comment
COMMENT ON VIEW s_university.v_student_full_info IS 'Complete student information with group, course, and specialty details';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'View [s_university.v_student_full_info] created successfully';
END $$;
