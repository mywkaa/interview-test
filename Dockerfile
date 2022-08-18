FROM python:3.8.9

RUN mkdir /app

COPY . /app/

RUN pip install -r /app/requirements.txt

WORKDIR /app/myapp

CMD [ "flask", "--debug", "run", "-h", "0.0.0.0"]
