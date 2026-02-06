FROM python:3.11-slim

WORKDIR /app

RUN  apt-get update && apt-get install -y gcc libpq-dev build-essential && apt-get clean
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modestwear/ .
COPY deploy.sh .
RUN chmod +x deploy.sh

EXPOSE 8000

CMD ["bash", "deploy.sh"]