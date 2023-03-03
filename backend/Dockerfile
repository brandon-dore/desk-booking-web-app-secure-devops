FROM python:3.9

LABEL name="backend"

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 8000 

# uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
CMD ["uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]