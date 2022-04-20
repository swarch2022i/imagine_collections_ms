FROM python:3.8.10
RUN mkdir /code
WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt

CMD ["sh", "-c", "python manage.py install_labels && python manage.py runserver 0.0.0.0:8000"]