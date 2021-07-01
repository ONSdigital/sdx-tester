FROM google/cloud-sdk:slim

RUN apt-get install kubectl
RUN apt-get update && apt-get install -y gnupg
COPY . /app
WORKDIR /app
RUN python3 -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
