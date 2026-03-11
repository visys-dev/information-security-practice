# Electronic Dean's Office

## Опис

REST API на базі **FastAPI + SQLite**.
Практична робота з дисципліни **"Безпека інформаційних систем"**.

Застосунок контейнеризовано за допомогою **Docker** та запускається через **Docker Compose**.

## Технології

* Python
* FastAPI
* SQLite
* SQLAlchemy
* Alembic
* Docker / Docker Compose
* **uv** — сучасний менеджер залежностей Python (альтернатива pip)

## Запуск

```bash
git clone https://github.com/visys-dev/information-security-practice.git
cd information-security-practice
docker compose up --build
```

Docker автоматично:

* встановлює залежності через **uv**
* запускає сервер **Uvicorn**
* відкриває API на порту **3010**

## Доступ

* API: http://localhost:3010
* Swagger документація: http://localhost:3010/docs
* ReDoc документація: http://localhost:3010/redoc

## Студент

Mishchenko Vitalii
Група: 231-on
