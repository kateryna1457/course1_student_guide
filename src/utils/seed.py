from datetime import date, timedelta
from typing import List, Dict
import random
from faker import Faker

from src.repositories import StudentRepository


fake_uk = Faker('uk_UA')
fake_en = Faker('en_US')


class DataGenerator:
    """Генератор тестових даних для студентів."""

    def __init__(self, repository: StudentRepository = None):
        """
        Ініціалізувати генератор.

        Args:
            repository: Репозиторій для роботи з БД
        """
        self.repository = repository or StudentRepository()

    def generate_student_id_number(self, group_name: str, year: int) -> str:
        """
        Згенерувати номер залікової книжки.

        Format: XX-NNNN (наприклад, CS-2024)

        Args:
            group_name: Назва групи (наприклад, "CS-11")
            year: Рік вступу

        Returns:
            Номер залікової книжки
        """
        prefix = group_name.split('-')[0]
        number = random.randint(1000, 9999)
        return f"{prefix}-{number}"

    def generate_phone_number(self) -> str:
        """
        Згенерувати український номер телефону.

        Format: +380XXXXXXXXX

        Returns:
            Номер телефону
        """
        operator_codes = ['50', '63', '66', '67', '68', '91', '92', '93', '94', '95', '96', '97', '98', '99']
        operator = random.choice(operator_codes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(7)])
        return f"+380{operator}{number}"

    def generate_birth_date(self) -> date:
        """
        Згенерувати дату народження (вік 17-25 років).

        Returns:
            Дата народження
        """
        today = date.today()
        years_ago = random.randint(17, 25)
        birth_year = today.year - years_ago

        birth_date = fake_uk.date_between(
            start_date=date(birth_year, 1, 1),
            end_date=date(birth_year, 12, 31)
        )
        return birth_date

    def generate_enrollment_date(self, birth_date: date, admission_year: int) -> date:
        """
        Згенерувати дату зарахування.

        Args:
            birth_date: Дата народження
            admission_year: Рік вступу з групи

        Returns:
            Дата зарахування
        """
        enrollment_date = date(admission_year, 9, 1)

        delta = timedelta(days=random.randint(-10, 10))
        return enrollment_date + delta

    def generate_student(self, group: Dict) -> Dict:
        """
        Згенерувати одного студента.

        Args:
            group: Словник з інформацією про групу

        Returns:
            Словник з даними студента
        """
        gender = random.choice(['M', 'F'])

        if gender == 'M':
            last_name = fake_uk.last_name_male()
            first_name = fake_uk.first_name_male()
            middle_name = fake_uk.middle_name_male()
        else:
            last_name = fake_uk.last_name_female()
            first_name = fake_uk.first_name_female()
            middle_name = fake_uk.middle_name_female()

        email_prefix = f"{first_name.lower()}.{last_name.lower()}"
        email_prefix_en = (
            email_prefix
            .replace('а', 'a').replace('б', 'b').replace('в', 'v')
            .replace('г', 'h').replace('ґ', 'g').replace('д', 'd')
            .replace('е', 'e').replace('є', 'ye').replace('ж', 'zh')
            .replace('з', 'z').replace('и', 'y').replace('і', 'i')
            .replace('ї', 'yi').replace('й', 'y').replace('к', 'k')
            .replace('л', 'l').replace('м', 'm').replace('н', 'n')
            .replace('о', 'o').replace('п', 'p').replace('р', 'r')
            .replace('с', 's').replace('т', 't').replace('у', 'u')
            .replace('ф', 'f').replace('х', 'kh').replace('ц', 'ts')
            .replace('ч', 'ch').replace('ш', 'sh').replace('щ', 'shch')
            .replace('ь', '').replace('ю', 'yu').replace('я', 'ya')
            .replace("'", '')
        )

        email_domains = ['example.com', 'student.edu.ua', 'university.ua', 'mail.com']
        email = f"{email_prefix_en}@{random.choice(email_domains)}"

        max_attempts = 10
        student_id_number = None

        for _ in range(max_attempts):
            candidate = self.generate_student_id_number(
                group['name'],
                group['admission_year']
            )

            if not self.repository.exists_student_id(candidate):
                student_id_number = candidate
                break

        if not student_id_number:
            import time
            student_id_number = f"{group['name'].split('-')[0]}-{int(time.time()) % 10000}"

        birth_date = self.generate_birth_date()
        enrollment_date = self.generate_enrollment_date(birth_date, group['admission_year'])

        phone = self.generate_phone_number() if random.random() < 0.8 else None

        return {
            'last_name': last_name,
            'first_name': first_name,
            'patronymic': middle_name,
            'student_id_number': student_id_number,
            'group_id': group['id'],
            'email': email,
            'phone': phone,
            'birth_date': birth_date,
            'enrollment_date': enrollment_date
        }

    def seed_students(self, count: int) -> List[int]:
        """
        Заповнити БД випадковими студентами.

        Args:
            count: Кількість студентів для генерації

        Returns:
            Список ID створених студентів

        Raises:
            ValueError: Якщо немає доступних груп
        """
        groups = self.repository.get_all_groups()

        if not groups:
            raise ValueError(
                "Немає доступних груп у базі даних. "
                "Переконайтеся що docker/tables/dml/ скрипти виконалися."
            )

        created_ids = []

        for i in range(count):
            group = random.choice(groups)

            student_data = self.generate_student(group)

            try:
                student_id = self.repository.create(student_data)
                created_ids.append(student_id)

                if (i + 1) % 10 == 0 or (i + 1) == count:
                    print(f"✓ Створено {i + 1}/{count} студентів")

            except Exception as e:
                print(f"✗ Помилка при створенні студента {i + 1}: {e}")
                continue

        return created_ids

    def get_statistics(self) -> Dict:
        """
        Отримати статистику БД.

        Returns:
            Словник зі статистикою
        """
        total_students = self.repository.count()
        total_groups = len(self.repository.get_all_groups())
        total_specialties = len(self.repository.get_all_specialties())
        total_courses = len(self.repository.get_all_courses())

        students_by_course = []
        for course in self.repository.get_all_courses():
            count = self.repository.count_by_course(course['id'])
            students_by_course.append({
                'course_number': course['course_number'],
                'course_name': course['name'],
                'count': count
            })

        return {
            'total_students': total_students,
            'total_groups': total_groups,
            'total_specialties': total_specialties,
            'total_courses': total_courses,
            'students_by_course': students_by_course
        }


def seed_database(count: int = 20) -> int:
    """
    Функція-хелпер для заповнення бази даних.

    Args:
        count: Кількість студентів для генерації

    Returns:
        Кількість створених студентів
    """
    generator = DataGenerator()
    created_ids = generator.seed_students(count)
    return len(created_ids)
