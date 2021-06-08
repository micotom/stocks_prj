FROM python:3.8-slim-buster

RUN mkdir /app

WORKDIR /app

COPY . /app/

RUN pip install -r requirements.txt

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 8000

CMD ["waitress-serve", "--port=8000", "app.wsgi:application"]