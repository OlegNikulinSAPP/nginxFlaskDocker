# Это как сказать: "Мы будем использовать специальные инструменты для нашей программы"
import os  # Инструмент для разговора с компьютером
from flask import Flask, jsonify  # Инструменты для создания веб-страниц
import psycopg2  # Инструмент для разговора с базой данных (как с картотекой)
from flask import request  # 📨 Нужно импортировать request!

# Создаем наше веб-приложение - как строим маленький домик в интернете
app = Flask(__name__)


def get_db_connection():
    """
        Это как ключ от картотеки с данными.

        Функция создает соединение с базой данных PostgreSQL.
        Она знает, где найти картотеку (хост), как она называется (database),
        и у кого есть ключ (user и password).

        Returns:
            Connection object: Ключ для доступа к картотеке
        """
    # psycopg2 - это специальный почтальон, который умеет разговаривать
    # с PostgreSQL (это такой умный домик с данными)
    # .connect - это как сказать почтальону:
    # "Пожалуйста, сходи к домику с данными и постучи в дверь!"
    conn = psycopg2.connect(                          # В скобках мы говорим почтальону:
        host='db',                                    # 🏠 Адрес домика с данными
        database=os.environ.get('POSTGRES_DB'),       # 📦 Какой ящик нам нужен
        user=os.environ.get('POSTGRES_USER'),         # 👦 Наше имя
        password=os.environ.get('POSTGRES_PASSWORD')  # 🔑 Секретный ключ
    )
    # Когда почтальон успешно постучался и его пустили внутрь,
    # он приносит нам волшебную трубку для разговора с домиком!
    # Эта трубка называется "conn" (соединение)
    return conn


@app.route('/')
def record_visit():
    """
    Это главная дверь нашего домика в интернете.

    Когда кто-то заходит на нашу страницу, эта функция:
    1. Открывает картотеку
    2. Создает таблицу для записей, если ее еще нет
    3. Добавляет новую запись о визите
    4. Считает все визиты
    5. Показывает результат

    Returns:
        JSON: Сообщение об успешной записи и общее количество визитов
    """
    # 🎒 Достаем все из волшебного рюкзака request!
    info = {
        'method': request.method,
        'path': request.path,
        'url': request.url,
        'args': dict(request.args),
        'headers': dict(request.headers),
        'cookies': dict(request.cookies),
        'remote_addr': request.remote_addr,
        'user_agent': str(request.user_agent),
        'is_secure': request.is_secure,
        'host': request.host,
    }

    # 🖨️ Печатаем в консоль
    print("=== ВОЛШЕБНЫЙ РЮКЗАК REQUEST ===")
    for key, value in info.items():
        print(f"{key}: {value}")
    print("=====================", flush=True)

    # Получаем ключ от картотеки
    conn = get_db_connection()
    # Создаем помощника, который будет писать в картотеке
    cur = conn.cursor()
    # Создаем папку для записей, если ее еще нет
    # "CREATE TABLE IF NOT EXISTS" = "Создай папку 'visits', если ее еще нет"
    # "visits" будет содержать номер записи (id) и время визита (timestamp)
    cur.execute('CREATE TABLE IF NOT EXISTS visits ('
                'id serial PRIMARY KEY, '
                'timestamp timestamptz'
                ');')
    # Добавляем новую запись о визите
    # "INSERT INTO visits" = "Запиши в папку 'visits'"
    # "VALUES (NOW())" = "текущее время"
    cur.execute('INSERT INTO visits (timestamp) VALUES (NOW());')
    # Сохраняем изменения в картотеке (как закрываем и запираем ящик)
    conn.commit()

    # Считаем все записи в папке
    # "SELECT COUNT(*)" = "Посчитай все записи"
    cur.execute('SELECT COUNT(*) FROM visits;')
    # Берем результат подсчета
    count = cur.fetchone()[0]  # fetchone() берет первую строку, [0] берет первое число
    # Убираем помощника и закрываем картотеку
    cur.close()
    conn.close()

    response = jsonify(message="Visit recorded!", total_visits=count)

    # 🎯 Полная информация об ответе
    print("\n" + "=" * 60)
    print("📨 FLASK ОТПРАВЛЯЕТ БРАУЗЕРУ:")
    print(f"Status: HTTP/1.1 {response.status_code}")
    print(f"Content-Type: {response.content_type}")
    print(f"Content-Length: {response.content_length} bytes")
    print(f"Headers: {dict(response.headers)}")
    print("Body:")
    print(response.get_data(as_text=True))
    print("=" * 60 + "\n", flush=True)

    return response


if __name__ == "__main__":
    """
        Это инструкция: "Когда включаем наш домик, сделай вот что..."

        Запускает веб-сервер, который:
        - Слушает все входящие подключения (host="0.0.0.0")
        - Работает на порту 5000 (как дверь номер 5000)
        - Показывает ошибки, если что-то сломается (debug=True)
        """
    app.run(host="0.0.0.0", port=5000, debug=True)
