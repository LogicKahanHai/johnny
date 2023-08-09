FROM amd64/python:3.9-bookworm

RUN python -m pip install rasa

WORKDIR /app
COPY . .

RUN rasa train nlu

USER 1001

ENTRYPOINT [ "rasa" ]

CMD [ "run", "--enable-api", "--cors", "*", "--port", "8080" ]