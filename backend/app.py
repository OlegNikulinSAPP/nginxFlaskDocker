import os
import time  # ✅ Импортируем время глобально
from flask import Flask, jsonify, request  # ✅ Все импорты тут
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


def create_logs_table():
    """Создает таблицу для логгирования запросов и ответов"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS request_logs (
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


def log_to_db(response, start_time):  # ✅ Убрали параметр request
    """Записывает информацию о запросе и ответе в базу данных"""
    # ✅ Используем глобальный request из Flask
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
            request.method,  # ✅ Используем глобальный request
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
        print(f"Ошибка при записи лога: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()


# Создаем таблицы при старте
create_logs_table()


@app.route('/api/visit')
def record_visit():
    start_time = time.time()

    # Печатаем информацию о запросе
    print("=== ВОЛШЕБНЫЙ РЮКЗАК REQUEST ===")
    print(f"Метод: {request.method}")
    print(f"Путь: {request.path}")
    print(f"URL: {request.url}")
    print(f"IP: {request.remote_addr}")
    print(f"Браузер: {request.user_agent}")
    print("=====================", flush=True)

    # Работа с базой данных
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id serial PRIMARY KEY, 
            timestamp timestamptz
        )
    ''')
    cur.execute('INSERT INTO visits (timestamp) VALUES (NOW());')
    conn.commit()

    cur.execute('SELECT COUNT(*) FROM visits;')
    count = cur.fetchone()[0]

    cur.close()
    conn.close()

    response = jsonify(message="Visit recorded!", total_visits=count)

    # ✅ Передаем только response и start_time
    log_to_db(response, start_time)

    return response


@app.route('/api/logs')
def show_logs():
    conn = get_db_connection()
    cur = conn.cursor()

    # Получаем описание колонок
    cur.execute('SELECT * FROM request_logs ORDER BY timestamp DESC LIMIT 50;')
    logs = cur.fetchall()

    # Получаем названия колонок
    colnames = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    # Преобразуем каждый кортеж в словарь
    logs_list = []
    for log in logs:
        log_dict = {}
        for i, value in enumerate(log):
            log_dict[colnames[i]] = value
        logs_list.append(log_dict)

    return jsonify(logs=logs_list)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
