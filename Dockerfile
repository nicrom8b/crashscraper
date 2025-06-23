FROM python:3.11

WORKDIR /app

COPY Pipfile Pipfile.lock* ./
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile

# Descargar recursos de NLTK necesarios
RUN pipenv run python -m nltk.downloader stopwords

COPY . .

EXPOSE 8000

CMD ["pipenv", "run", "start"] 