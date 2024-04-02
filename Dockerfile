FROM python:3.11-slim

COPY ./requirements /tmp/requirements
RUN pip install -r /tmp/requirements/deploy.txt

EXPOSE 8080

COPY ./server /server

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8080"]
