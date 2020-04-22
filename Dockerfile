FROM python:3.7

RUN adduser -D microblog

WORKDIR /home/microblog

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY scraper.py boot.sh ./

ENV FLASK_APP scraper.py

RUN chown -R scraperapp:scraperapp ./
USER scraperapp

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
