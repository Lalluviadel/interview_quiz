FROM python:3.8.6

WORKDIR /usr/src/interview_quiz

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && pip3 install --upgrade pip
RUN apt-get install -y libpq-dev postgresql postgresql-contrib python3-dev gcc musl-dev
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN apt install -y netcat

ENTRYPOINT ["/usr/src/interview_quiz/entrypoint.sh"]
