FROM python:3.14-slim

WORKDIR /app_code

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen

COPY . .

RUN mkdir -p /app_code/data

EXPOSE 3010

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3010"]