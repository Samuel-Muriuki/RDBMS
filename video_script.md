# Video Demonstration Script for SimpleDB

**Duration**: 5-7 minutes  
**Purpose**: Showcase the RDBMS functionality for Pesapal Junior Dev Challenge 2026

---

## Introduction (30 seconds)

**[Screen: Terminal/IDE with project open]**

"Hi! I'm Samuel Muriuki, and this is my submission for the Pesapal Junior Developer Challenge 2026. I've built a fully functional relational database management system from scratch in Python, complete with SQL support, an interactive REPL, and a beautiful web application."

---

## Part 1: Project Overview (45 seconds)

**[Screen: README.md or project structure]**

"Let me show you what I've built:

- A custom SQL parser that tokenizes and parses SQL commands
- A storage engine with hash-based indexing for O(1) lookups
- Support for PRIMARY KEY, UNIQUE, and NOT NULL constraints
- Full CRUD operations with WHERE, ORDER BY, and LIMIT clauses
- An interactive REPL for database operations
- And a modern web application that uses the database as its backend

The entire system has 36 passing tests covering all components."

---

## Part 2: REPL Demonstration (2 minutes)

**[Screen: Terminal]**

### Start the REPL
```bash
python3 -m simpledb.repl
```

"Let's start with the interactive REPL. I'll create a database for managing students and courses."

### Create Tables
```sql
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    age INT
);
```

"Notice the constraints - id is a primary key, name cannot be null, and email must be unique."

```sql
CREATE TABLE courses (
    id INT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    credits INT
);
```

### Insert Data
```sql
INSERT INTO students VALUES (1, 'Alice Johnson', 'alice@university.edu', 20);
INSERT INTO students VALUES (2, 'Bob Smith', 'bob@university.edu', 22);
INSERT INTO students VALUES (3, 'Charlie Brown', 'charlie@university.edu', 19);
INSERT INTO students VALUES (4, 'Diana Prince', 'diana@university.edu', 21);
```

```sql
INSERT INTO courses VALUES (101, 'Database Systems', 4);
INSERT INTO courses VALUES (102, 'Web Development', 3);
INSERT INTO courses VALUES (103, 'Data Structures', 4);
```

### Query Data
```sql
SELECT * FROM students;
```

"Beautiful table formatting! Now let's try some filtering:"

```sql
SELECT name, email FROM students WHERE age >= 20 ORDER BY name ASC;
```

"We can also use LIMIT:"

```sql
SELECT * FROM students LIMIT 2;
```

### Update Data
```sql
UPDATE students SET age = 23 WHERE name = 'Bob Smith';
SELECT * FROM students WHERE id = 2;
```

### Test Constraints
```sql
INSERT INTO students VALUES (5, 'Eve Adams', 'alice@university.edu', 20);
```

"Notice it fails - the email must be unique! This shows our constraint enforcement is working."

### Relational Features & Aggregates
```sql
SELECT students.name, grades.grade FROM students INNER JOIN grades ON students.id = grades.student_id;
SELECT COUNT(*) FROM students;
```

"As you can see, SimpleDB supports multi-table joins and aggregate functions, just like a production RDBMS."

### Delete Data
```sql
DELETE FROM students WHERE age < 20;
SELECT * FROM students;
```

### Special Commands
```sql
.tables
.schema students
```

"These special commands help us inspect the database structure."

```sql
.exit
```

---

## Part 3: Web Application Demo (2-3 minutes)

**[Screen: Terminal]**

### Start the Web App
```bash
cd webapp
python3 app.py
```

**[Screen: Browser at localhost:5000]**

"Now let's look at the web application. I've built a task manager that uses SimpleDB as its backend."

### Show the UI
"Notice the modern design:
- Dark mode with glassmorphism effects
- Smooth gradient backgrounds
- Beautiful animations and transitions
- Fully responsive layout"

### Create Tasks
**[Create 3-4 tasks with different statuses]**

"Let me create a few tasks... Each task is being stored in our SimpleDB database using INSERT statements."

### Update Task Status
**[Click the status button to cycle through statuses]**

"I can update task status with a single click - this uses UPDATE queries behind the scenes."

### SQL Console
**[Scroll to SQL Console section]**

"Here's something cool - an interactive SQL console right in the browser!"

```sql
SELECT * FROM tasks ORDER BY created_at DESC;
```

"We can run any SQL query directly."

```sql
SELECT title, status FROM tasks WHERE status = 'completed';
```

### Delete Task
**[Delete a task]**

"And deletion works perfectly with our DELETE statements."

---

## Part 4: Code Architecture (1 minute)

**[Screen: IDE showing code structure]**

"Let me quickly show you the architecture:

**[Open simpledb/parser.py]**
- Here's the SQL parser - it tokenizes input and builds an abstract syntax tree

**[Open simpledb/storage.py]**
- The storage engine manages tables, indexes, and constraints
- Hash-based indexes provide O(1) lookup for primary keys

**[Open simpledb/executor.py]**
- The executor takes parsed commands and executes them on the storage engine

**[Open tests/ directory]**
- And we have comprehensive tests - all 36 passing"

---

## Part 5: Testing (30 seconds)

**[Screen: Terminal]**

```bash
pytest tests/ -v
```

"Let's run the test suite... All 36 tests passing! This covers:
- Parser functionality
- Storage engine with constraints
- Full query execution
- Edge cases and error handling"

---

## Part 6: Deployment (45 seconds)

**[Screen: Browser showing Vercel dashboard or deployed app]**

"The application is ready for deployment on Vercel. I've configured it for serverless deployment with:
- vercel.json for routing configuration
- Serverless function entry point
- All dependencies specified

The deployment process is simple:
1. Push to GitHub
2. Connect to Vercel
3. Deploy - it takes less than a minute

And the app is live for anyone to interact with!"

---

## Conclusion (30 seconds)

**[Screen: README or project overview]**

"To summarize, I've built:
- A working RDBMS with SQL support
- Hash-based indexing and constraint enforcement
- An interactive REPL
- A beautiful, modern web application
- Comprehensive test coverage
- Production-ready deployment configuration

All the code is well-documented and follows best practices. This project demonstrates my understanding of:
- Data structures and algorithms
- Parsing and language design
- Database concepts
- Web development
- Testing and quality assurance

Thank you for watching! I'm excited about the opportunity to join Pesapal and contribute to building amazing products."

---

## Recording Tips

1. **Preparation**:
   - Clear your terminal history
   - Close unnecessary applications
   - Test all commands beforehand
   - Have a clean database state

2. **During Recording**:
   - Speak clearly and at a moderate pace
   - Pause briefly between sections
   - Show enthusiasm and confidence
   - If you make a mistake, just continue (or re-record that section)

3. **Screen Recording Tools**:
   - **Linux**: OBS Studio, SimpleScreenRecorder, Kazam
   - **Command**: `obs` or `simplescreenrecorder`

4. **Video Editing** (optional):
   - Add intro/outro slides
   - Speed up long-running commands
   - Add captions for key points

5. **Upload**:
   - YouTube (unlisted or public)
   - Loom
   - Google Drive
   - Include link in your application

---

## Quick Setup Before Recording

```bash
# Clean up any existing database files
rm -f simpledb.json webapp.json

# Ensure all dependencies are installed
pip install -r requirements.txt

# Run tests to verify everything works
pytest tests/ -v

# Practice the demo once before recording
```

---

## Alternative: Shorter Version (3 minutes)

If you need a shorter demo:
1. Introduction (20s)
2. REPL Demo - Basic CRUD (1m)
3. Web App Demo (1m)
4. Show Tests Running (20s)
5. Conclusion (20s)

Focus on the most impressive features and keep transitions quick!
