FROM python:3.14-slim

WORKDIR /app_code

RUN pip install --no-cache-dir uv

ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# копіюємо код
COPY . .

# директорія для SQLite
RUN mkdir -p /app_code/data

EXPOSE 3010

CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3010"]