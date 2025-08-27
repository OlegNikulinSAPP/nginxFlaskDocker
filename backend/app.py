import os, time, psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db_connection():
    """ Устанавливает соединение с базой данных PostgreSQL.
    :return: Объект соединения с базой данных PostgreSQL (psycopg2.connection) """

    conn = psycopg2.connect(
        host='db',
        database=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
    )

    return conn


def create_logs_table():
    """Создает таблицу для логирование запросов и ответов"""

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXIST request_logs (
        id serial PRIMARY KEY,
        timestamp timestamptz DEFAULT NOW(),
        method VARCHAR(10),
        path VARCHAR(500),
        client_ip VARCHAR(45),
        user_agent TEXT,
        request_headers TEXT,
        response_status VARCHAR(10),
        response_headers TEXT,
        response_body TEXT,
        processing_time_ms INTEGER
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()


def log_to_db(response, start_time):
    """Записывает информацию о запросе и ответе в базу данных"""
    end_time = time.time()
    processing_time_ms = int((end_time - start_time) * 1000)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute('''
            INSERT INTO request_logs
            (method, path, client_ip, user_agent, request_headers, 
            response_status, response_headers, response_body, processing_time_ms)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            request.method,
            request.path,
            request.remote_addr,
            str(request.user_agent),
            str(dict(request.headers)),
            response.status_code,
            str(dict(response.headers)),
            response.get_data(as_text=True),
            processing_time_ms
        ))
        conn.commit()
    except Exception as e:
        print(f'Ошибка при записи лога: {e}')
        conn.rollback()
    finally:
        cur.close()
        conn.close()
