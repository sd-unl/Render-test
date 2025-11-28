import os
import random
import string
from flask import Flask, render_template_string, jsonify
from sqlalchemy import create_engine, text

app = Flask(__name__)

# 1. GET DATABASE URL FROM ENVIRONMENT VARIABLE
# On Render, we will set this variable in the dashboard so we don't expose the password in code.
DB_URL = os.environ.get("DATABASE_URL")

def generate_random_string(length=12):
    """Generates a random string of letters and numbers"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# 2. THE WEBPAGE (Frontend)
@app.route('/')
def home():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Supabase Tester</title>
        <style>
            body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background-color: #f4f4f9; }
            button { padding: 20px 40px; font-size: 20px; background-color: #3ecf8e; color: white; border: none; border-radius: 8px; cursor: pointer; transition: 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            button:hover { background-color: #34b27b; transform: translateY(-2px); }
            button:active { transform: translateY(0); }
            #status { margin-top: 20px; font-size: 18px; font-weight: bold; color: #333; }
        </style>
    </head>
    <body>
        <h1>Supabase Connection Test</h1>
        <button onclick="sendSignal()">🚀 Send Random Data</button>
        <div id="status">Waiting for input...</div>

        <script>
            async function sendSignal() {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = "⏳ Sending...";
                statusDiv.style.color = "blue";

                try {
                    const response = await fetch('/send-data', { method: 'POST' });
                    const result = await response.json();

                    if (response.ok) {
                        statusDiv.innerHTML = "✅ Success! Sent: " + result.data;
                        statusDiv.style.color = "green";
                    } else {
                        statusDiv.innerHTML = "❌ Error: " + result.error;
                        statusDiv.style.color = "red";
                    }
                } catch (error) {
                    statusDiv.innerHTML = "❌ Network Error";
                    statusDiv.style.color = "red";
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

# 3. THE BACKEND LOGIC
@app.route('/send-data', methods=['POST'])
def send_data():
    if not DB_URL:
        return jsonify({"error": "Database URL is missing in Environment Variables"}), 500

    random_data = generate_random_string()

    try:
        # Connect to Database
        engine = create_engine(DB_URL)
        
        with engine.connect() as connection:
            # A. Create a table if it doesn't exist yet
            create_table_sql = text("""
                CREATE TABLE IF NOT EXISTS signal_tests (
                    id SERIAL PRIMARY KEY,
                    random_content TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            connection.execute(create_table_sql)
            
            # B. Insert the random data
            insert_sql = text("INSERT INTO signal_tests (random_content) VALUES (:val)")
            connection.execute(insert_sql, {"val": random_data})
            
            # Commit the transaction
            connection.commit()

        return jsonify({"message": "Data saved", "data": random_data}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
