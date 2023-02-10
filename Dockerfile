FROM python:3.11
RUN apt-get install -y gnupg
RUN python3 -m pip install --upgrade pip
RUN pip install pipenv