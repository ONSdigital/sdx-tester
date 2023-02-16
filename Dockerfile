FROM python:3.11
RUN apt-get install -y gnupg
COPY . /app
WORKDIR /app
RUN python3 -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install