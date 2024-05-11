FROM python:3.10-slim

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir

COPY ./app /app

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]