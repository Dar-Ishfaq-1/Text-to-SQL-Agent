"""
Text-to-SQL Agent Backend
Flask API with Google Gemini AI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import json
import re
from datetime import datetime
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configure Google AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

DB_PATH = "sample_database.db"

def init_database():
    """Initialize sample database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    
    cursor.execute("SELECT COUNT(*) FROM customers")
    if cursor.fetchone()[0] == 0:
        customers = [
            ('John Doe', 'john@example.com', 'New York', '2024-01-15'),
            ('Jane Smith', 'jane@example.com', 'New York', '2024-02-20'),
            ('Alice Brown', 'alice@example.com', 'Boston', '2024-01-10'),
            ('Bob Wilson', 'bob@example.com', 'Seattle', '2024-03-05'),
            ('Charlie Davis', 'charlie@example.com', 'Chicago', '2024-02-15'),
        ]
        cursor.executemany(
            "INSERT INTO customers (name, email, city, created_at) VALUES (?, ?, ?, ?)",
            customers
        )
        
        orders = [
            (1, 'Widget Pro', 299.99, '2024-03-01'),
            (1, 'Gadget Plus', 149.99, '2024-03-15'),
            (2, 'Tool Set', 89.99, '2024-03-10'),
            (3, 'Premium Widget', 399.99, '2024-03-20'),
            (4, 'Basic Kit', 49.99, '2024-03-05'),
        ]
        cursor.executemany(
            "INSERT INTO orders (customer_id, product, amount, order_date) VALUES (?, ?, ?, ?)",
            orders
        )
        
        products = [
            ('Widget Pro', 'Electronics', 299.99, 50),
            ('Gadget Plus', 'Electronics', 149.99, 100),
            ('Tool Set', 'Tools', 89.99, 75),
            ('Premium Widget', 'Electronics', 399.99, 25),
            ('Basic Kit', 'Tools', 49.99, 150),
        ]
        cursor.executemany(
            "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
            products
        )
    
    conn.commit()
    conn.close()

def get_schema_info():
    """Get database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    schema = {}
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        schema[table_name] = {
            'columns': [col[1] for col in columns],
            'types': {col[1]: col[2] for col in columns}
        }
    
    conn.close()
    return schema

def build_prompt(user_query, schema):
    """Build prompt for Gemini"""
    schema_str = "Database Schema:\n\n"
    for table, info in schema.items():
        schema_str += f"Table: {table}\n"
        schema_str += "Columns:\n"
        for col in info['columns']:
            col_type = info['types'][col]
            schema_str += f"  - {col} ({col_type})\n"
        schema_str += "\n"
    
    prompt = f"""{schema_str}

User Request: {user_query}

Generate a SQL query that answers the user's request.

IMPORTANT RULES:
1. Use correct table and column names from schema
2. Use proper SQLite syntax
3. For "which/what" questions about counts, use GROUP BY with COUNT
4. For "top N" queries, use ORDER BY with LIMIT
5. For aggregations, use SUM, COUNT, AVG, etc.
6. Only generate SELECT queries

EXAMPLES:
- "Which city has most customers?" → SELECT city, COUNT(*) as count FROM customers GROUP BY city ORDER BY count DESC LIMIT 1;
- "Top 5 products by price" → SELECT * FROM products ORDER BY price DESC LIMIT 5;
- "Show all customers" → SELECT * FROM customers;

Return ONLY a JSON object with this exact format (no markdown, no backticks):
{{
    "sql": "your SQL query here",
    "explanation": "what the query does"
}}"""

    return prompt

def validate_sql(sql):
    """Validate SQL query"""
    sql_upper = sql.upper()
    
    dangerous = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'UPDATE', 'INSERT']
    for keyword in dangerous:
        if keyword in sql_upper:
            return False, f"Forbidden operation: {keyword}"
    
    if not sql_upper.strip().startswith('SELECT'):
        return False, "Only SELECT queries allowed"
    
    return True, "Valid"

def execute_query(sql):
    """Execute SQL query"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        start_time = datetime.now()
        cursor.execute(sql)
        results = cursor.fetchall()
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        results_list = [dict(row) for row in results]
        
        conn.close()
        return {
            'success': True,
            'results': results_list,
            'row_count': len(results_list),
            'execution_time': execution_time
        }
    except Exception as e:
        conn.close()
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/api/schema', methods=['GET'])
def get_schema():
    """Get database schema"""
    try:
        schema = get_schema_info()
        return jsonify({
            'success': True,
            'schema': schema
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/query', methods=['POST'])
def process_query():
    """Process natural language query"""
    try:
        data = request.json
        user_query = data.get('query', '')
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Query required'
            }), 400
        
        schema = get_schema_info()
        prompt = build_prompt(user_query, schema)
        
        # Call Gemini
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        response_text = response.text
        
        # Parse JSON response
        cleaned = response_text.strip()
        cleaned = re.sub(r'```json\s*', '', cleaned)
        cleaned = re.sub(r'```\s*', '', cleaned)
        
        try:
            response_data = json.loads(cleaned)
        except:
            match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned)
            if match:
                response_data = json.loads(match.group(0))
            else:
                return jsonify({
                    'success': False,
                    'error': 'Could not parse AI response'
                }), 500
        
        sql = response_data.get('sql', '')
        explanation = response_data.get('explanation', '')
        
        is_valid, msg = validate_sql(sql)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': msg,
                'sql': sql
            }), 400
        
        result = execute_query(sql)
        
        if result['success']:
            return jsonify({
                'success': True,
                'sql': sql,
                'explanation': explanation,
                'results': result['results'],
                'row_count': result['row_count'],
                'execution_time': result['execution_time']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'sql': sql
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'ai_model': 'Google Gemini 1.5 Flash',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    init_database()
    print("✅ Database initialized!")
    print("✅ Using Google Gemini AI")
    print("✅ Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)