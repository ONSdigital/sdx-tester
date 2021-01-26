FROM python:3.8-slim
RUN apt-get update && apt-get install -y gnupg
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -U -r /app/requirements.txt
EXPOSE 5000
CMD ["python", "./run.py"]
