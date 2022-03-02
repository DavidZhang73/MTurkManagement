FROM python:3.8
MAINTAINER DavidZ

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE MTurkManagement.prod-settings
ARG MONGO_PASSWORD
ENV MONGO_PASSWORD=$MONGO_PASSWORD
ARG POSTGRESQL_PASSWORD
ENV POSTGRESQL_PASSWORD=$POSTGRESQL_PASSWORD

RUN mkdir -p /MTurkManagement
WORKDIR /MTurkManagement
ADD . /MTurkManagement

RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install https://projects.unbit.it/downloads/uwsgi-lts.tar.gz

RUN python manage.py collectstatic --noinput && \
    python manage.py migrate

EXPOSE 8000

ENTRYPOINT ["uwsgi", "--ini", "/MTurkManagement/config/uwsgi.ini"]
