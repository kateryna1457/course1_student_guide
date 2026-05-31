"""
Константи для додатка.

Централізоване зберігання всіх магічних чисел та констант.
"""

# Validation constants - Age limits
MIN_STUDENT_AGE = 15  # Мінімальний вік студента
MAX_STUDENT_AGE = 100  # Максимальний вік студента

# Validation constants - String lengths
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 100
MIN_EMAIL_LENGTH = 3
MAX_EMAIL_LENGTH = 255
MIN_STUDENT_ID_LENGTH = 3
MAX_STUDENT_ID_LENGTH = 20
MIN_GROUP_NAME_LENGTH = 4
MAX_GROUP_NAME_LENGTH = 20
MIN_SPECIALTY_CODE_LENGTH = 2
MAX_SPECIALTY_CODE_LENGTH = 10

# Course numbers
MIN_COURSE_NUMBER = 1
MAX_COURSE_NUMBER = 6

# Admission year limits
MIN_ADMISSION_YEAR = 1900

# Database connection pool
DB_POOL_MIN_CONNECTIONS = 1
DB_POOL_MAX_CONNECTIONS = 10

# API Rate limiting
RATE_LIMIT_REQUESTS = 100  # Кількість запитів
RATE_LIMIT_PERIOD = "1 minute"  # Період часу
RATE_LIMIT_REQUESTS_CREATE = 20  # Кількість запитів для створення записів
RATE_LIMIT_PERIOD_CREATE = "1 minute"  # Період для створення записів

# Pagination defaults
DEFAULT_PAGE_OFFSET = 0
DEFAULT_PAGE_LIMIT = 20
MAX_PAGE_LIMIT = 100
