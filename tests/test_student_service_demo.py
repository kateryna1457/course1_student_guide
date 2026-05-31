"""
Демонстрація роботи StudentService.

Показує основні операції CRUD.
"""

import sys
import os
from datetime import date

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services import StudentService
from src.utils import ValidationError


def main():
    """Демонстрація StudentService."""
    print("=" * 60)
    print("STUDENT SERVICE DEMO")
    print("=" * 60)
    print()

    service = StudentService()

    try:
        # 1. Get reference data
        print("1. Getting reference data...")
        groups = service.get_groups()
        specialties = service.get_specialties()
        courses = service.get_courses()

        print(f"   ✓ Groups: {len(groups)}")
        print(f"   ✓ Specialties: {len(specialties)}")
        print(f"   ✓ Courses: {len(courses)}")

        if not groups:
            print("   ✗ No groups found! Run seed data first.")
            return

        first_group_id = groups[0]['id']
        print(f"   ✓ Using group: {groups[0]['name']} (ID: {first_group_id})")
        print()

        # 2. Create student
        print("2. Creating a new student...")
        student_data = {
            'last_name': 'Shevchenko',
            'first_name': 'Taras',
            'patronymic': 'Hryhorovych',
            'student_id_number': 'TEST-2024',
            'group_id': first_group_id,
            'email': 'shevchenko@example.com',
            'phone': '+380501234567',
            'birth_date': date(2000, 3, 9)
        }

        # Check if student already exists
        if not service.student_id_number_available('TEST-2024'):
            print("   ⚠ Student TEST-2024 already exists, skipping creation")
            # Try to find existing student
            students, _ = service.search_students({'query': 'TEST-2024'})
            if students:
                student_id = students[0].id
                print(f"   ✓ Found existing student with ID: {student_id}")
        else:
            student_id = service.create_student(student_data)
            print(f"   ✓ Student created with ID: {student_id}")

        print()

        # 3. Get student
        print("3. Getting student details...")
        student = service.get_student(student_id)

        if student:
            print(f"   ✓ Name: {student.get_full_name()}")
            print(f"   ✓ Email: {student.email}")
            print(f"   ✓ Group: {student.group_name}")
            print(f"   ✓ Specialty: {student.specialty_name}")
            print(f"   ✓ Course: {student.course_number}")
        else:
            print("   ✗ Student not found")

        print()

        # 4. List students
        print("4. Listing students...")
        students, total = service.list_students(offset=0, limit=5)
        print(f"   ✓ Found {total} students (showing first {len(students)}):")

        for s in students:
            print(f"      - {s.get_full_name()} ({s.student_id_number}) - {s.group_name}")

        print()

        # 5. Search students
        print("5. Searching students...")
        results, count = service.search_students({'query': 'Shevchenko'})
        print(f"   ✓ Found {count} students matching 'Shevchenko'")

        for s in results:
            print(f"      - {s.get_full_name()} - {s.email}")

        print()

        # 6. Update student
        print("6. Updating student...")
        updated = service.update_student(student_id, {
            'phone': '+380671234567',
            'email': 'taras.shevchenko@example.com'
        })

        if updated:
            print("   ✓ Student updated successfully")
            student = service.get_student(student_id)
            print(f"   ✓ New email: {student.email}")
            print(f"   ✓ New phone: {student.phone}")
        else:
            print("   ✗ Update failed")

        print()

        # 7. Statistics
        print("7. Getting statistics...")
        stats = service.get_statistics()
        print(f"   ✓ Total students: {stats['total_students']}")
        print(f"   ✓ Total groups: {stats['total_groups']}")
        print(f"   ✓ Total specialties: {stats['total_specialties']}")

        if stats.get('students_by_course'):
            print("   ✓ Students by course:")
            for course_stat in stats['students_by_course']:
                print(f"      - Course {course_stat['course_number']}: {course_stat['count']} students")

        print()

        # 8. Export (optional - commented out to avoid file creation)
        # print("8. Exporting data...")
        # count_json = service.export_to_json('data/students_demo.json')
        # count_csv = service.export_to_csv('data/students_demo.csv')
        # print(f"   ✓ Exported {count_json} students to JSON")
        # print(f"   ✓ Exported {count_csv} students to CSV")
        # print()

        print("=" * 60)
        print("DEMO COMPLETED ✓")
        print("=" * 60)

    except ValidationError as e:
        print(f"\n✗ Validation error: {e}")
    except ValueError as e:
        print(f"\n✗ Value error: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
