FROM python:3.12-slim-bullseye

WORKDIR /app 

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt


RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    dirmngr \
    debian-archive-keyring

    RUN curl -fsSL https://pgp.mongodb.com/server-7.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/7.0 main" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list



ENV SEED_DATA /app/seed
ENV BACKUP_FOLDER /data/backup



RUN apt-get update && apt-get install -y \
    mongodb-org-tools \
    && rm -rf /var/lib/apt/lists/*


EXPOSE 3096

CMD exec uvicorn main:app --host 0.0.0.0 --port 3096 --workers $(expr $(nproc) \* 2 + 1)

