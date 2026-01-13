"""
Flask web application demonstrating SimpleDB usage.

A task management app with CRUD operations.
"""

import os
import sys
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simpledb.supabase_storage import SupabaseDatabase
from simpledb.executor import QueryExecutor
from simpledb.exceptions import SimpleDBException

app = Flask(__name__)

# Initialize database with Supabase
db = SupabaseDatabase()
executor = QueryExecutor(db)

# Initialize tasks table if it doesn't exist
try:
    db.get_table('tasks')
except:
    executor.execute("""
        CREATE TABLE tasks (
            id INT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description VARCHAR(500),
            status VARCHAR(20) NOT NULL,
            created_at VARCHAR(50)
        );
    """)


@app.route('/')
def index():
    """Render main application page."""
    return render_template('index.html')


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
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
    data = request.json
    
    # Get next ID
    result = executor.execute("SELECT * FROM tasks;")
    next_id = len(result['rows']) + 1 if result['success'] else 1
    
    # Insert task
    title = data.get('title', '').replace("'", "''")
    description = data.get('description', '').replace("'", "''")
    status = data.get('status', 'pending')
    
    from datetime import datetime
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    sql = f"""
        INSERT INTO tasks VALUES (
            {next_id},
            '{title}',
            '{description}',
            '{status}',
            '{created_at}'
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
    data = request.json
    sql = data.get('sql', '')
    
    if not sql:
        return jsonify({'success': False, 'error': 'No SQL provided'}), 400
    
    result = executor.execute(sql)
    return jsonify(result)


# For Vercel serverless deployment
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
