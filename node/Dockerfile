# Use an official Python runtime as the base image
FROM amd64/python:3.9-buster as project_env

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip setuptools \
    && pip install -r requirements.txt

FROM project_env

COPY gunicorn_conf.py app.py app_config.py app_utils.py init_data.py /app/

# Set the entrypoint command
CMD ["gunicorn", "--conf", "/app/gunicorn_conf.py", "app:app"]