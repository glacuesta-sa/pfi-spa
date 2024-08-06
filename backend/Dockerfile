# Dependencies  stage
FROM python:3.12 AS dependencies

# copy and install dependencies
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Build stage
FROM python:3.12

# workdir is /app, copy all files
WORKDIR /app
COPY . /app

# copy dependencies and set pip paths
COPY --from=dependencies /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

ENV FLASK_APP=src/app.py
ENV FLASK_ENV=development
ENV FLASK_DEBUG=0

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Switch to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

# app and debug ports
EXPOSE 5000 5768

# Run app.py when the container launches
CMD ["flask", "run", "--host=0.0.0.0"]