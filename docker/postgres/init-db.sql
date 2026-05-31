\echo 'Step 1: Creating schema...'
\ir schemas/ddl/s_university.sql

\echo 'Step 2: Creating tables...'
\ir tables/ddl/t_specialties.sql
\ir tables/ddl/t_courses.sql
\ir tables/ddl/t_groups.sql
\ir tables/ddl/t_students.sql

\echo 'Step 3: Creating views...'
\ir views/ddl/v_student_full_info.sql

\echo 'Step 4: Loading initial data...'
\ir tables/dml/t_courses.sql
\ir tables/dml/t_specialties.sql
\ir tables/dml/t_groups.sql

\echo 'Step 5: Granting permissions...'
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA s_university TO student_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA s_university TO student_user;
GRANT USAGE ON SCHEMA s_university TO student_user;

\echo 'Database initialization completed successfully!'
