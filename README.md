# SimpleDB - Relational Database Management System

A fully functional relational database management system (RDBMS) built from scratch in Python, featuring SQL-like query language, interactive REPL, and a beautiful web application demo.

**Built for the Pesapal Junior Dev Challenge 2026**

[![Tests](https://img.shields.io/badge/tests-36%2F36%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🌟 Features

### Core Database Engine
- **SQL Parser**: Custom-built tokenizer and parser supporting SQL-like syntax
- **Storage Engine**: In-memory tables with JSON persistence
- **Indexing**: Hash-based O(1) lookups for primary keys and unique columns
- **Constraints**: PRIMARY KEY, UNIQUE, NOT NULL enforcement
- **CRUD Operations**: Full Create, Read, Update, Delete support
- **Relational Features**: `INNER JOIN` support for linking tables
- **Aggregates**: `COUNT(*)` support for data summary
- **Query Features**: WHERE clauses, ORDER BY, LIMIT, aliases (AS)

### Data Types
- `INT` - Integer numbers
- `VARCHAR(n)` - Variable-length strings (max n characters)
- `BOOLEAN` - True/False values

### SQL Commands Supported
```sql
CREATE TABLE table_name (column_name type constraints, ...);
DROP TABLE table_name;
INSERT INTO table_name VALUES (value1, value2, ...);
INSERT INTO table_name (col1, col2) VALUES (val1, val2);
SELECT * FROM table_name;
SELECT col1, col2 FROM table_name WHERE condition;
UPDATE table_name SET col = value WHERE condition;
DELETE FROM table_name WHERE condition;
SELECT col1, col2 FROM table1 INNER JOIN table2 ON table1.id = table2.fk_id;
SELECT COUNT(*) FROM table_name;
SELECT col AS alias FROM table_name;
```

### Interactive REPL
- Multi-line SQL input
- Formatted table output
- Special commands: `.tables`, `.schema`, `.help`, `.exit`
- Persistent storage across sessions

### Web Application
- 🎨 **Beautiful Modern UI**: Dark mode with glassmorphism effects
- ✨ **Premium Design**: Gradient backgrounds, smooth animations
- 📝 **Task Manager**: Full CRUD demo application
- 💻 **SQL Console**: Execute custom queries directly in the browser
- 🚀 **Vercel Ready**: Configured for serverless deployment

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/Samuel-Muriuki/RDBMS.git
cd RDBMS
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🚀 Usage

### Interactive REPL

Start the interactive SQL shell:
```bash
python3 -m simpledb.repl
```

Example session:
```sql
SimpleDB> CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50) NOT NULL, age INT);
Table 'users' created successfully

SimpleDB> INSERT INTO users VALUES (1, 'Alice', 25);
1 row inserted

SimpleDB> INSERT INTO users VALUES (2, 'Bob', 30);
1 row inserted

SimpleDB> SELECT * FROM users;
+----+-------+-----+
| id | name  | age |
+----+-------+-----+
| 1  | Alice | 25  |
| 2  | Bob   | 30  |
+----+-------+-----+
2 row(s) selected.

SimpleDB> UPDATE users SET age = 26 WHERE name = 'Alice';
1 row(s) updated

SimpleDB> SELECT * FROM users WHERE age > 25 ORDER BY name ASC;
+----+-------+-----+
| id | name  | age |
+----+-------+-----+
| 1  | Alice | 26  |
| 2  | Bob   | 30  |
+----+-------+-----+
2 row(s) selected.

SimpleDB> .exit
Goodbye!
```

### Web Application

Run the Flask web app locally:
```bash
cd webapp
python3 app.py
```

Then open your browser to: `http://localhost:5000`

The web app features:
- Task creation and management
- Real-time CRUD operations
- Interactive SQL console
- Beautiful, responsive UI

### Supabase Configuration

The application uses Supabase PostgreSQL for persistent storage. To configure it:

1. **Copy the environment template**:
   ```bash
   cp .env.example .env.local
   ```

2. **Fill in your credentials in `.env.local`**:
   ```bash
   # Supabase Configuration
   # Copy this file to .env.local and fill in your actual values

   # Supabase URL
   SUPABASE_URL=your_supabase_url_here

   # Supabase Keys
   SUPABASE_ANON_KEY=your_anon_key_here
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

   # PostgreSQL Connection
   POSTGRES_HOST=your_postgres_host_here
   POSTGRES_DATABASE=postgres
   POSTGRES_USER=your_postgres_user_here
   POSTGRES_PASSWORD=your_postgres_password_here
   POSTGRES_PORT=5432

   # Direct PostgreSQL URL (non-pooling for better compatibility)
   DATABASE_URL=your_database_url_here
   ```

## 🌐 Deployment to Vercel

### Prerequisites
- GitHub account (you already have this!)
- Vercel account (free) - Sign up at [vercel.com](https://vercel.com)

### Deployment Steps

1. **Push your code to GitHub** (already configured in this repo)

2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com) and sign in with GitHub
   - Click "Add New Project"
   - Import your `RDBMS` repository
   - Vercel will auto-detect the configuration from `vercel.json`

3. **Deploy**:
   - Click "Deploy"
   - Wait for deployment to complete (usually < 1 minute)
   - Your app will be live at `https://your-project.vercel.app`

4. **Share the link**:
   - Copy the deployment URL
   - Include it in your job application

**That's it!** No additional configuration needed. The `vercel.json` and `api/index.py` files are already configured for serverless deployment.

### Alternative: Deploy via CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow the prompts
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
pytest tests/ -v
```

Test coverage:
- **36 tests** covering all components
- Parser tests (13 tests)
- Storage engine tests (12 tests)
- Executor integration tests (11 tests)

All tests passing ✅

## 🏗️ Architecture

```
┌─────────────────┐
│   User Input    │
│   (SQL Query)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Parser      │
│  (Tokenizer +   │
│   AST Builder)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Executor     │
│  (Query Plan +  │
│   Validation)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Storage Engine  │
│  (Tables +      │
│   Indexes)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSON Storage   │
│  (Persistence)  │
└─────────────────┘
```

## 📁 Project Structure

```
RDBMS/
├── simpledb/              # Core database engine
│   ├── __init__.py
│   ├── exceptions.py      # Custom exceptions
│   ├── parser.py          # SQL tokenizer and parser
│   ├── storage.py         # Storage engine (tables, indexes)
│   ├── executor.py        # Query executor
│   └── repl.py            # Interactive REPL
├── webapp/                # Web application demo
│   ├── app.py             # Flask application
│   ├── templates/
│   │   └── index.html     # Beautiful UI
│   └── static/
│       └── styles.css     # Premium styling
├── api/                   # Vercel serverless functions
│   └── index.py           # Entry point for Vercel
├── tests/                 # Test suite
│   ├── test_parser.py
│   ├── test_storage.py
│   └── test_executor.py
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
└── README.md             # This file
```

## 🎯 Design Decisions

### 1. In-Memory Storage with JSON Persistence
- **Why**: Simple, readable, sufficient for demo purposes
- **Trade-off**: Not suitable for large datasets, but perfect for showcasing concepts

### 2. Custom SQL Parser
- **Why**: Demonstrates understanding of parsing, tokenization, and AST construction
- **Trade-off**: Limited SQL feature set vs. full SQL compliance

### 3. Hash-Based Indexing
- **Why**: O(1) lookup performance for primary keys
- **Trade-off**: Memory overhead vs. query speed

### 4. No Transactions
- **Why**: Acceptable simplification for this challenge
- **Future**: Could add transaction support with rollback

### 5. Single-User Model
- **Why**: Simplifies concurrency concerns
- **Future**: Could add locking mechanisms for multi-user support

## 🚧 Future Enhancements

Potential improvements (not required for challenge):
- [ ] More aggregate functions (SUM, AVG, MIN, MAX)
- [ ] GROUP BY and HAVING clauses
- [ ] More data types (FLOAT, DATE, TIMESTAMP)
- [ ] Transaction support (BEGIN, COMMIT, ROLLBACK)
- [ ] B-tree indexes for range queries
- [ ] Query optimization and execution plans
- [ ] Multi-user concurrency control

## 🙏 Acknowledgments

This project was built with assistance from AI coding tools (Claude/Gemini) for:
- Code structure suggestions
- Best practices recommendations
- Documentation formatting
- Test case generation

All core logic, architecture decisions, and implementation were guided by my understanding and requirements for the Pesapal challenge.

## 📝 License

MIT License - feel free to use this code for learning purposes.

## 👤 Author

**Samuel Muriuki**

Built for the Pesapal Junior Developer Challenge 2026

---

## 📊 Quick Stats

- **Lines of Code**: ~2,500
- **Test Coverage**: 36 tests, all passing
- **Development Time**: Focused sprint implementation
- **Technologies**: Python, Flask, HTML/CSS/JavaScript
- **Deployment**: Vercel (serverless)

---

**Note**: This is a demonstration project built for a job application challenge. It showcases database concepts, SQL parsing, data structures, and web development skills.
