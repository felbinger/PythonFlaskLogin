ARG BASE_IMG=nicof2000/pythonflasklogin:build
FROM ${BASE_IMG}

ENV MYSQL_HOSTNAME=mariadb
ENV MYSQL_PORT=3306
ENV MYSQL_USERNAME=root
ENV MYSQL_DATABASE=example
ENV REDIS_HOSTNAME=redis
ENV REDIS_PORT=6379
ENV REDIS_DATABASE=0

EXPOSE 80
WORKDIR /app
COPY . /app


CMD ["gunicorn", "--workers", "4", "wsgi:application", "--bind", "0.0.0.0:80", "--log-syslog", "--log-level", "DEBUG"]
