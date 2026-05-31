INSERT INTO s_university.t_courses (course_number, name) VALUES
    (1, 'First Year'),
    (2, 'Second Year'),
    (3, 'Third Year'),
    (4, 'Fourth Year'),
    (5, 'Fifth Year'),
    (6, 'Sixth Year')
ON CONFLICT (course_number) DO NOTHING;

DO $$
DECLARE
    course_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO course_count FROM s_university.t_courses;
    RAISE NOTICE 'Initial data loaded: % courses in [s_university.t_courses]', course_count;
END $$;
