FROM python:3.9

LABEL name="backend"

WORKDIR /code

COPY . /code

RUN pip install pipenv

RUN pipenv requirements > requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN cd app

EXPOSE 8000 

# uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]