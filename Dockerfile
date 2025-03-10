FROM laudio/pyodbc:3.0.0

RUN apt-get update && apt-get install -y build-essential

RUN pip install --upgrade pip

RUN apt-get install unixodbc unixodbc-dev -y

COPY . /app

RUN rm /app/db.sqlite3

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["scripts/entrypoint.sh"]
