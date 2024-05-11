FROM python:3.10-slim

WORKDIR /app

COPY ./app /app

COPY ./requirements.txt /app

EXPOSE 8081
EXPOSE 50000

RUN pip install -r requirements.txt --no-cache-dir

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "30000"]