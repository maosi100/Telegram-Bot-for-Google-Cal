FROM python:3.11-slim-buster
WORKDIR /bot
COPY requirements.txt /bot
RUN pip install -r requirements.txt
RUN mkdir utilities
COPY *.py /bot
COPY token.pickle /bot
COPY event_categories.txt /bot
COPY utilities/credentials.json /bot/utilities/
COPY utilities/calendar_id.txt /bot/utilities/