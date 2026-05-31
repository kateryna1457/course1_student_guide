INSERT INTO s_university.t_specialties (name, code, description) VALUES
    (
        'Computer Science',
        '122',
        'Fundamental computer science, algorithms, and computational theory'
    ),
    (
        'Software Engineering',
        '121',
        'Design, development, and maintenance of software systems'
    ),
    (
        'Cybersecurity',
        '125',
        'Information security, cryptography, and protection of computer systems'
    ),
    (
        'Information Technology',
        '126',
        'IT infrastructure, systems administration, and technical support'
    ),
    (
        'System Analysis',
        '124',
        'Analysis, design, and optimization of information systems'
    ),
    (
        'Computer Engineering',
        '123',
        'Computer hardware, embedded systems, and digital electronics'
    ),
    (
        'Data Science',
        '122-DS',
        'Data analysis, machine learning, and statistical modeling'
    ),
    (
        'Artificial Intelligence',
        '122-AI',
        'AI algorithms, neural networks, and intelligent systems'
    )
ON CONFLICT (name) DO NOTHING;

-- Success message
DO $$
DECLARE
    specialty_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO specialty_count FROM s_university.t_specialties;
    RAISE NOTICE 'Initial data loaded: % specialties in [s_university.t_specialties]', specialty_count;
END $$;
