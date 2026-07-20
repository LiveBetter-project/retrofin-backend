FROM python:3.10.14-slim-bookworm

WORKDIR /usr/src/backend

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc libpq-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache-dir --upgrade pip
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8010

COPY ./entrypoint.sh .
RUN chmod +x /usr/src/backend/entrypoint.sh

RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /usr/src/backend

USER appuser

ENTRYPOINT ["/usr/src/backend/entrypoint.sh"]

