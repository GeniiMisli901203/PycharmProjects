FROM python:3.12-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

# update pip python
RUN pip3 install -U pip

# install packages for the project
RUN pip3 install -r requirements.txt

EXPOSE 8080
