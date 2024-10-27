# --------- requirements ---------

FROM python:3.10.12 AS requirements-stage

WORKDIR /tmp

# Specify the desired version of Poetry
ENV POETRY_VERSION=1.1.12

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export --no-interaction --no-ansi -f requirements.txt --output requirements.txt --without-hashes


# --------- final image build ---------
FROM python:3.10.12

WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the wait-for-it script
COPY wait-for-it.sh /code/wait-for-it.sh
RUN chmod +x /code/wait-for-it.sh


COPY ./src/app /code/app

# Start the application using wait-for-it to ensure dependencies are ready
CMD ["/code/wait-for-it.sh", "db:5432", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# Alternative to run with gunicorn:
# CMD ["/code/wait-for-it.sh", "db:5432", "--", "gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
