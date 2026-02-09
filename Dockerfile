FROM python:3.11-slim

ENV AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
ENV CONTAINER_NAME=datasets
ENV BLOB_NAME=All_Diets.csv

WORKDIR /app

COPY requirements.txt .
COPY data_analysis_azure.py .
COPY All_Diets.csv .

RUN pip install --no-cache-dir -r requirements.txt

RUN npm install -g azurite

RUN mkdir -p /azurite/data

EXPOSE 10000 10001 10002

CMD azurite --blobHost 0.0.0.0 --location /azurite/data & \
    sleep 3 && \
    mkdir -p /azurite/data/datasets && \
    cp /app/All_Diets.csv /azurite/data/datasets/All_Diets.csv && \
    python /app/data_analysis_azure.py
