FROM python:3.11
RUN apt-get install -y gnupg

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin

COPY . /app
WORKDIR /app
RUN python3 -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install