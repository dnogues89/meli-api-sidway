FROM python:3.10

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && apt-get install -y build-essential

RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN pip install --upgrade pip

RUN apt-get install unixodbc unixodbc-dev -y


COPY . /app

RUN rm /app/db.sqlite3

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["scripts/entrypoint.sh"]
