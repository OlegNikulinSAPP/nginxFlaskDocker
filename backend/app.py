import os
from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host='db',
        database=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD')
    )
    return conn

@app.route('/')
def record_visit():
    """Returns the number of times the page has been visited."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS visits ('
                'id serial PRIMARY KEY, '
                'timestamp timestamptz'
                ');')
    cur.execute('INSERT INTO visits (timestamp) VALUES (NOW());')
    conn.commit()

    cur.execute('SELECT COUNT(*) FROM visits;')
    count = cur.fetchone()[0]
    cur.close()
    conn.close()

    return jsonify(message="Visit recorded successfully!", total_visits=count)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
