# Student Directory CLI - Demo Commands

This document contains sample commands for demonstrating the Student Directory CLI application.

## Setup & Initial Data

```bash
# 1. Seed database with test students (generate 50 random students)
python -m src.cli seed --count 50

# 2. Show application statistics
python -m src.cli stats
```

## Viewing Students

```bash
# 3. List first 20 students
python -m src.cli list

# 4. List with pagination (skip first 20, show next 15)
python -m src.cli list --offset 20 --limit 15

# 5. Show groups
python -m src.cli groups

# 6. Show specialties
python -m src.cli specialties
```

## Searching Students

```bash
# 7. Search by last name
python -m src.cli search "Іванов"

# 8. Search by group name
python -m src.cli search --group "IT-11"

# 9. Search by course number (1st year students)
python -m src.cli search --course 1

# 10. Search by specialty code (Computer Science)
python -m src.cli search --specialty "122"

# 11. Combined search (last name + group)
python -m src.cli search "Петров" --group "CS-11"

# 12. Combined search (specialty + course)
python -m src.cli search --specialty "122" --course 1
```

## Student Details

```bash
# 13. Show detailed info about specific student (use actual student ID from list)
python -m src.cli show CS-2024-001

# 14. Show another student
python -m src.cli show SE-2024-015
```

## Adding Students (Interactive)

```bash
# 15. Add new student interactively
python -m src.cli add

# Follow the interactive prompts:
# - Last name: Коваленко
# - First name: Олег
# - Patronymic: Петрович
# - Student ID: CS-2026-050
# - Group ID: (select from displayed list)
# - Email: kovalenko@example.com
# - Phone: +380501234567
# - Birth date: 2005-03-15
```

## Updating Students

```bash
# 16. Update student data (use existing student ID)
python -m src.cli update CS-2024-001

# Follow prompts to update email/phone
```

## Deleting Students

```bash
# 17. Delete student (use existing student ID)
python -m src.cli delete CS-2024-999

# Confirm deletion when prompted
```

## Export Data

```bash
# 18. Export all students to JSON
python -m src.cli export json

# 19. Export all students to CSV
python -m src.cli export csv

# 20. Export filtered students to JSON (specific group)
python -m src.cli export json --group "CS-11"

# 21. Export filtered students to CSV (specific course)
python -m src.cli export csv --course 1

# 22. Export with multiple filters (query + group)
python -m src.cli export json --query "Іванов" --group "IT-11"

# 23. Export by specialty code
python -m src.cli export csv --specialty "122" --course 2
```

## Advanced Searches

```bash
# 24. Search with pagination
python -m src.cli search --course 2 --offset 0 --limit 10

# 25. Wide search with high limit
python -m src.cli search "Петренко" --limit 100
```

---

## Quick Demo Flow (Recommended Order)

This is the recommended sequence for a complete demonstration:

```bash
# Step 1: Initialize data
python -m src.cli seed --count 30
python -m src.cli stats

# Step 2: View data
python -m src.cli list --limit 10
python -m src.cli groups
python -m src.cli specialties

# Step 3: Search examples
python -m src.cli search --course 1
python -m src.cli search --group "IT-11"

# Step 4: View details (use real student ID from previous output)
python -m src.cli show CS-2024-001

# Step 5: Export
python -m src.cli export json --course 1
python -m src.cli export csv

# Step 6: Final stats
python -m src.cli stats
```

---

## Available Commands

- `add` - Add a new student (interactive)
- `list` - Show list of students with pagination
- `show` - Show detailed information about a student
- `search` - Search students by criteria
- `update` - Update student data (interactive)
- `delete` - Delete a student
- `export` - Export students to JSON or CSV with optional filters
- `groups` - Show list of all groups
- `specialties` - Show list of all specialties
- `stats` - Show statistics
- `seed` - Fill database with test data

## Export Files

All exported files are saved in the `demo/exports/` directory with timestamps:
- `students_YYYY-MM-DD_HHMMSS.json`
- `students_YYYY-MM-DD_HHMMSS.csv`

## Features

- Rich colored tables and panels
- Interactive prompts for data entry
- Progress indicators for long operations
- Input validation
- Pagination support
- Flexible filtering and search
- Multiple export formats
