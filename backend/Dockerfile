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

# app and debug ports
EXPOSE 5000 5001

# Run app.py when the container launches
CMD ["python", "-Xfrozen_modules=off", "-m", "flask", "run", "--host=0.0.0.0"]