FROM python:3.10.14-bullseye

WORKDIR /usr/src/backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-server-dev-all gcc python3-dev musl-dev g++ netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

COPY ./entrypoint.sh .
RUN chmod +x /usr/src/backend/entrypoint.sh

ENTRYPOINT ["/usr/src/backend/entrypoint.sh"]

