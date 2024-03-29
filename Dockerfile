FROM python:3.9
WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
ENV FLASK_APP=app.py
CMD flask run --host 0.0.0.0 port $PORT