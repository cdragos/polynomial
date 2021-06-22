FROM python:3.8.5-slim-buster

# Set work directory
WORKDIR /usr/src/polynomial

# Install pipenv and compilation dependencies
RUN pip install pipenv

COPY Pipfile* /usr/src/polynomial
RUN pipenv install --dev --system --deploy --ignore-pipfile

# Force the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED 1
# Force python to not write .pyc files on the import of source modules
ENV PYTHONDONTWRITEBYTECODE 1

EXPOSE 5000

CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0"]
