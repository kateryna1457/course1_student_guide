INSERT INTO s_university.t_groups (name, specialty_id, course_id, admission_year)
SELECT
    g.name,
    s.id AS specialty_id,
    c.id AS course_id,
    g.admission_year
FROM (VALUES
    ('CS-11', 'Computer Science', 1, 2024),
    ('SE-11', 'Software Engineering', 1, 2024),
    ('CY-11', 'Cybersecurity', 1, 2024),
    ('IT-11', 'Information Technology', 1, 2024),

    ('CS-21', 'Computer Science', 2, 2023),
    ('SE-21', 'Software Engineering', 2, 2023),
    ('SA-21', 'System Analysis', 2, 2023),
    ('IT-21', 'Information Technology', 2, 2023),

    ('CS-31', 'Computer Science', 3, 2022),
    ('SE-31', 'Software Engineering', 3, 2022),
    ('CY-31', 'Cybersecurity', 3, 2022),
    ('CE-31', 'Computer Engineering', 3, 2022),

    ('CS-41', 'Computer Science', 4, 2021),
    ('SE-41', 'Software Engineering', 4, 2021),
    ('DS-41', 'Data Science', 4, 2021),
    ('AI-41', 'Artificial Intelligence', 4, 2021),

    ('CS-51', 'Computer Science', 5, 2020),
    ('SE-51', 'Software Engineering', 5, 2020)
) AS g(name, specialty_name, course_number, admission_year)
JOIN s_university.t_specialties s ON s.name = g.specialty_name
JOIN s_university.t_courses c ON c.course_number = g.course_number
ON CONFLICT (name) DO NOTHING;

DO $$
DECLARE
    group_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO group_count FROM s_university.t_groups;
    RAISE NOTICE 'Initial data loaded: % groups in [s_university.t_groups]', group_count;
END $$;
