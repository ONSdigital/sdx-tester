FROM python:3.8-slim
#COPY --from=lachlanevenson/k8s-kubectl:v1.10.3 /usr/local/bin/kubectl /usr/local/bin/kubectl
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -U -r /app/requirements.txt
EXPOSE 5000
CMD ["python", "./run.py"]
