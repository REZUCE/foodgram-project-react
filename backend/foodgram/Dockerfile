FROM python:3.7-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get -y install python3-pip

RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:7000"]