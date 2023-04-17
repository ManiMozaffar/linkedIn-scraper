FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
COPY src/ .

EXPOSE 8000 5432 6379

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]