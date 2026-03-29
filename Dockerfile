FROM python:3.14-slim

WORKDIR /app_code

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv pip install --system .

COPY . .

RUN mkdir -p /app_code/data

EXPOSE 3010

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3010"]