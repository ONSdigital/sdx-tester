FROM google/cloud-sdk:348.0.0-slim
# note that newer versions of cloud sdk don't recognise our version of collate
# error: unknown object type *v1beta1.CronJob
RUN apt-get install kubectl
RUN apt-get update && apt-get install -y gnupg
COPY . /app
WORKDIR /app
RUN python3 -m pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --deploy --ignore-pipfile
