import os
from flask import Flask, jsonify
import psycopg2

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

    # Получаем ключ от картотеки
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
