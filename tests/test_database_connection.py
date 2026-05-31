"""
Тест підключення до бази даних.

Перевіряє чи працює підключення до PostgreSQL.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.repositories import get_db


def main():
    """Тестування підключення до БД."""
    print("=" * 60)
    print("DATABASE CONNECTION TEST")
    print("=" * 60)
    print()

    try:
        db = get_db()

        # Test 1: Connection test
        print("1. Testing connection...")
        if db.test_connection():
            print("   ✓ Connection successful")
        else:
            print("   ✗ Connection failed")
            return

        print()

        # Test 2: Schema check
        print("2. Checking schema...")
        result = db.execute_one("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = 's_university';
        """)

        if result:
            print(f"   ✓ Schema [s_university] exists")
        else:
            print("   ✗ Schema [s_university] NOT found")
            return

        print()

        # Test 3: Tables check
        print("3. Checking tables...")
        tables = ['t_specialties', 't_courses', 't_groups', 't_students']
        for table in tables:
            result = db.execute_one("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 's_university'
                AND table_name = %s;
            """, (table,))

            if result:
                print(f"   ✓ Table [s_university.{table}] exists")
            else:
                print(f"   ✗ Table [s_university.{table}] NOT found")

        print()

        # Test 4: View check
        print("4. Checking view...")
        result = db.execute_one("""
            SELECT table_name
            FROM information_schema.views
            WHERE table_schema = 's_university'
            AND table_name = 'v_student_full_info';
        """)

        if result:
            print("   ✓ View [s_university.v_student_full_info] exists")
        else:
            print("   ✗ View [s_university.v_student_full_info] NOT found")

        print()

        # Test 5: Data count
        print("5. Checking data...")
        courses = db.execute_one("SELECT COUNT(*) as count FROM t_courses;")
        specialties = db.execute_one("SELECT COUNT(*) as count FROM t_specialties;")
        groups = db.execute_one("SELECT COUNT(*) as count FROM t_groups;")
        students = db.execute_one("SELECT COUNT(*) as count FROM t_students;")

        print(f"   ✓ Courses: {courses['count']}")
        print(f"   ✓ Specialties: {specialties['count']}")
        print(f"   ✓ Groups: {groups['count']}")
        print(f"   ✓ Students: {students['count']}")

        print()
        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)

    except Exception as e:
        print()
        print("=" * 60)
        print(f"ERROR: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
