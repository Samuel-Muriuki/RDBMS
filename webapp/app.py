"""
Flask web application demonstrating SimpleDB usage.

A task management app with CRUD operations.
"""

import os
import sys
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
else:
    load_dotenv() # Fallback to standard environment variables (Vercel)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Flask
app = Flask(__name__)

# Initialize placeholders
db = None
executor = None
db_error = None
db_initialized = False

def init_db():
    global db, executor, db_error, db_initialized
    if db_initialized:
        return
    
    try:
        from simpledb.supabase_storage import SupabaseDatabase
        from simpledb.executor import QueryExecutor
        
        db = SupabaseDatabase()
        executor = QueryExecutor(db)

        # Initialize database tables
        try:
            # Force schema refresh if tasks table is old (missing category_id)
            try:
                tasks_table = db.get_table('tasks')
                if len(tasks_table.columns) < 6:
                    print("Upgrading 'tasks' table schema...")
                    db.drop_table('tasks')
            except:
                pass

            # Categories table with IF NOT EXISTS
            executor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INT PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL
                );
            """)
            
            # Check if categories already seeded
            cat_check = executor.execute("SELECT COUNT(*) as count FROM categories;")
            if cat_check['success'] and cat_check['rows'][0]['count'] == 0:
                executor.execute("INSERT INTO categories (id, name) VALUES (1, 'Work');")
                executor.execute("INSERT INTO categories (id, name) VALUES (2, 'Personal');")
                executor.execute("INSERT INTO categories (id, name) VALUES (3, 'Urgent');")
        except Exception as e:
            print(f"Error initializing categories/schema: {e}")

        try:
            # Tasks table with IF NOT EXISTS
            executor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description VARCHAR(500),
                    status VARCHAR(20) NOT NULL,
                    created_at VARCHAR(50),
                    category_id INT
                );
            """)
        except Exception as e:
            print(f"Error initializing tasks: {e}")

        db_initialized = True
    except Exception as e:
        print(f"CRITICAL: Database initialization failed: {e}")
        db_error = str(e)
        db_initialized = True # Mark as "tried" even if failed

@app.before_request
def ensure_db():
    init_db()


@app.route('/')
def index():
    """Render main application page."""
    return render_template('index.html', db_error=db_error)


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    if not executor:
        return jsonify({'success': False, 'error': f'Database not connected: {db_error}'}), 503
        
    result = executor.execute("SELECT * FROM tasks ORDER BY id DESC;")
    
    if result['success']:
        return jsonify({
            'success': True,
            'tasks': result['rows']
        })
    else:
        return jsonify(result), 400


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    if not executor:
        return jsonify({'success': False, 'error': f'Database not connected: {db_error}'}), 503
        
    data = request.json
    
    # Get next ID
    result = executor.execute("SELECT id FROM tasks ORDER BY id DESC LIMIT 1;")
    next_id = 1
    if result['success'] and result['rows']:
        next_id = result['rows'][0]['id'] + 1
    
    # Insert task
    title = data.get('title', '').replace("'", "''")
    description = data.get('description', '').replace("'", "''")
    status = data.get('status', 'pending')
    category_id = data.get('category_id', 1) # Default to 1 (Work)
    
    from datetime import datetime
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    sql = f"""
        INSERT INTO tasks VALUES (
            {next_id},
            '{title}',
            '{description}',
            '{status}',
            '{created_at}',
            {category_id}
        );
    """
    
    result = executor.execute(sql)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Task created',
            'id': next_id
        })
    else:
        return jsonify(result), 400


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    if not executor:
        return jsonify({'success': False, 'error': f'Database not connected: {db_error}'}), 503
        
    data = request.json
    
    updates = []
    if 'title' in data:
        title = data['title'].replace("'", "''")
        updates.append(f"title = '{title}'")
    if 'description' in data:
        description = data['description'].replace("'", "''")
        updates.append(f"description = '{description}'")
    if 'status' in data:
        updates.append(f"status = '{data['status']}'")
    
    if not updates:
        return jsonify({'success': False, 'error': 'No updates provided'}), 400
    
    sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = {task_id};"
    
    result = executor.execute(sql)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Task updated'
        })
    else:
        return jsonify(result), 400


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    if not executor:
        return jsonify({'success': False, 'error': f'Database not connected: {db_error}'}), 503
        
    sql = f"DELETE FROM tasks WHERE id = {task_id};"
    
    result = executor.execute(sql)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'Task deleted'
        })
    else:
        return jsonify(result), 400


@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute a custom SQL query."""
    if not executor:
        return jsonify({'success': False, 'error': f'Database not connected: {db_error}'}), 503
        
    data = request.json
    sql = data.get('sql', '')
    
    if not sql:
        return jsonify({'success': False, 'error': 'No SQL provided'}), 400
    
    result = executor.execute(sql)
    return jsonify(result)


# For Vercel serverless deployment
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
